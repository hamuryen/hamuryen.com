# AI Agents Are Distributed Systems. Treat Them Like One.

*What happens when a tool succeeds, the response gets lost, and your agent tries again?*

Imagine a support agent handling a refund.

It reads the ticket, checks the order, and calls the refund API. The payment service records the refund. Then the connection drops before the response gets back.

The agent sees a timeout. Retrying sounds reasonable, but the first refund may already be on its way. A second request could issue another one. Asking the model to think harder won't tell you whether the payment service committed the transaction.

This is the part of building agents that interests me. I've spent much of my career working on backend services, video pipelines, and infrastructure. When I look at an agent calling several tools to finish a task, I recognize a lot of the same problems.

Once an agent calls remote tools and changes data in other services, its work spans several systems. Something can succeed in one place and fail in another. A process can die halfway through the job.

Adding a model gives that system a new way to choose its next step. The old failure modes are still there.

## The timeout tells you less than you think

After a timeout, several things could have happened. The request never reached the service. The service rejected it. The refund succeeded, but the response was lost. The service might even still be processing it.

From the caller's side, these can look exactly the same.

The refund operation needs an idempotency key: a stable ID for this particular action. Every retry sends the same key. The receiving service uses it to recognize repeat requests and avoid issuing another refund.

The important word is *stable*. If your tool wrapper creates a new UUID every time it runs, every retry looks like a new refund.

Application code should create and save that key before making the first request. It belongs to the business operation, with its customer, order, amount, and currency. Reusing it with different details should fail.

For example, the job might save an operation ID of `refund-op-7842`. All three attempts use `refund-op-7842`. Even if the model proposes the refund again in different words, the application must recognize the existing operation. A fresh tool call doesn't automatically mean a new business action.

AWS explains this contract in [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/). Check the provider's retention rules too. [Stripe, for example, allows keys to be removed after at least 24 hours](https://docs.stripe.com/api/idempotent_requests). An old job can't assume that its key still protects it.

There is a catch: saving a key in your own database isn't enough when the action happens somewhere else. Your worker can still crash after the external service succeeds and before you save its response.

The service performing the action needs to support deduplication, or give you a reliable way to look up what happened. An empty search result isn't proof of failure if the first request might still be running. Some jobs need to stop for investigation. An unknown outcome is a valid state. Pretending it means “failed” can get expensive.

## A chat history is a poor job database

Suppose the agent's conversation contains this line:

> I have processed the refund and will now notify the customer.

That tells you what the model said. Before showing the customer a success message, I want a receipt from the payment service.

For a job like this, I would store the proposed action, its validated inputs, the approval if one was needed, the operation ID, and the confirmed external result. The conversation can help explain the decision. The job record tells the application what it can safely do next.

This also changes how you handle a restart. A replacement worker should be able to load the job and see that the refund is confirmed but the notification is still pending. It shouldn't have to reread a conversation and guess.

I'd keep the state names plain: proposed, approved, running, confirmed, outcome unknown, failed. Moving a refund to “confirmed” requires evidence from the payment service. A confident sentence from the model doesn't qualify.

## Put a boundary around the model's decision

The model is useful when a request needs interpretation. A customer writes three paragraphs about a damaged item, and the agent works out which order they mean and what help they want.

Once it proposes a refund, regular application code can take over much of the work.

Does this order belong to the customer? Is the amount valid? Has it already been refunded? Does the current user have permission? Is approval required?

These checks belong at the tool boundary, where they run regardless of what the prompt says.

The flow I would start with looks like this:

```
Read the request
    -> Ask the model for a proposed action
    -> Validate the action in code
    -> Save the proposal and operation ID
    -> Get approval when required
    -> Execute through a controlled tool
    -> Record the confirmed result
    -> Tell the customer what happened
```

This leaves the model room to handle messy language without giving it ownership of every business rule.

It also makes failure easier to explain. “The amount exceeds the allowed refund” is something you can test and show to a user. A long conversation where the model talks itself into a different amount is much harder to reason about.

## Where Temporal fits

Long-running video jobs have a similar shape. A request may pass through export, processing, storage, and notification. Some steps take time. Some fail. Restarting the entire chain can repeat expensive work.

That is the kind of problem where a workflow system becomes useful.

With Temporal, I would keep the coordination in a Workflow and put model calls and external API calls in Activities. Temporal records execution history so workers can rebuild workflow state after a failure. The [workflow code must be deterministic](https://docs.temporal.io/workflow-definition): replaying the same recorded history must produce the same sequence of commands.

The distinction matters for agents. A fresh model call can produce a different answer. During recovery, a recorded Activity result lets the workflow reuse the earlier decision. An Activity whose completion wasn't recorded may still run again, so the uncertainty hasn't disappeared.

Temporal also doesn't make a refund API safe to retry. If the payment succeeds and the Activity worker dies before reporting completion, another attempt can call that API again. The [Activity execution documentation](https://docs.temporal.io/activity-execution) covers this retry behavior. The operation ID still needs to travel all the way to the service that performs the refund.

I wouldn't add Temporal to every agent project. For a short task with a few steps, a database job table and a worker may be enough. You still have to design job claiming, retries, and recovery, but that can be a reasonable amount of code.

Once jobs wait for people, span several services, or need careful recovery across many steps, I'd look much more closely at a workflow engine.

## Human approval becomes stale

“Ask a human first” sounds like a complete solution until the human takes two days to answer.

During those two days, someone else might refund the order. The customer's request might change. The person who started the job might lose access.

A saved approval should refer to a specific action: this order, this amount, this currency, this version of the proposal. If the proposal changes, the old approval should no longer apply.

Before execution, the system should check current permissions and business conditions again. Those checks also need protection against concurrent changes at the service performing the action. A check in the agent process alone leaves a gap between checking and doing.

I would give approvals an expiry time too. Otherwise, an old job can wake up weeks later and perform something nobody is expecting anymore.

The interface should show what is waiting, who needs to respond, and what will happen after approval. “Agent is thinking” is a bad description of a job that has been waiting for a manager since Tuesday.

## Give retries an owner and a budget

An agent can retry at several levels without anyone intending it.

The HTTP client retries. The tool wrapper retries. The workflow retries the Activity. Then the model sees an error and decides to try the tool again.

If three layers each make three attempts, one logical action can turn into 27 downstream calls. During an outage, that extra load makes recovery harder.

I'd choose where retry policy lives and keep the other layers visible. Temporary failures can use bounded retries with increasing delays and jitter. Invalid input and permission failures should usually go back for correction. An uncertain write needs reconciliation before another attempt unless the receiving API can safely deduplicate it.

The agent also needs limits on the whole job: tool calls, elapsed time, model spend, and repeated attempts at the same action. AWS covers the service-side reasoning in its guidance on [controlling retry calls](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_limit_retries.html).

The exact limits depend on the task. The application should enforce them outside the model. A prompt saying “don't spend too much” is hard to put on a dashboard.

## Debug the job from its receipts

When a customer asks why they received two notifications, the final assistant message won't be enough.

I want to follow one job ID through the proposal, tool attempts, external requests, and results. Each attempt should have its own ID, while retries of the same business action keep the same operation ID.

Record the model and prompt version as well. They help explain why an action was proposed. Keep sensitive content out of general logs; store only what you need with appropriate access and retention.

Then measure the outcome of the job. Did the requested task finish? How long did it take? How many jobs are stuck waiting? How many have an unknown external outcome? How much did each completed task cost?

A successful model response is only one event in that chain. The payment receipt and the delivery status tell you whether the customer actually got what they asked for.

Adding more agents makes those IDs even more useful. If two agents pick up the same ticket, they need a shared way to recognize work already in progress. I'd start with one agent and add another when a specific part of the job benefits from it.

## The test I'd run before shipping

Take the refund flow and make the payment service return success. Kill the worker immediately afterward, before it saves the result.

Restart it.

Does it issue another refund? Does it find the first one? Does it stop with an unknown outcome? Can you tell which happened without reading every log line?

That one test exercises a boundary that a happy-path demo never touches.

I would also run the same job on two workers, deliver the same approval twice, and change the order while approval is pending. Then make a tool time out repeatedly and check that the job eventually stops within its budget.

You can run most of these with a fake model returning a fixed proposal. That makes the recovery behavior easier to test. Separately, test the model's decisions against examples of ambiguous requests, missing information, and actions it shouldn't propose.

Both kinds of tests matter. A system can reliably execute the wrong decision. It can also make the right decision and lose track of the result.

Before shipping, I want an answer to this question: if the process dies after an external action, what will the next worker do?

For our refund, it loads the saved operation ID, checks the payment service, finds the existing receipt, and continues with the notification. If it can't establish what happened, it leaves the refund alone and flags the job for review.

Once that works, I'd feel much better about letting the agent handle the next ticket.

---

*I'm Burak Hamuryen, a software engineer in Berlin working on distributed systems, real-time video processing, and AI infrastructure. More at [hamuryen.com](https://hamuryen.com).*
