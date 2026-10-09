# Your Kafka Consumers Are Becoming a Workflow Engine

*Retries are the easy part. Try cancelling work that has already started.*

![Video job cards move through a branching mechanical workflow; an orange gate stops one branch while another continues toward completion.](assets/kafka-workflow-engine-cover.png)

A user requests a video export, waits a few minutes, then clicks Cancel. The UI confirms it. Twenty minutes later, an email arrives: your export is ready.

Every message may have been delivered correctly. The renderer finished its job. The notification consumer handled the completion event. The cancellation consumer updated its own record. The system still did something the user had asked it to stop doing.

This is a hypothetical example, drawn from the kinds of backend and video systems I work on. It is a useful way to examine a design that often starts innocently: a few Kafka consumers, each responsible for one step, connected by topics. As requirements accumulate, the consumers acquire timers, retry rules, cancellation flags, and recovery scripts. Eventually, someone has to explain what the whole operation is doing.

A recent [discussion about using Kafka as a workflow execution engine](https://www.reddit.com/r/apachekafka/comments/1w6gv9m/we_used_kafka_as_workflow_execution_engine/) raised this same boundary. Kafka can remain a good part of the architecture. The question is where the application stores the decisions that must survive a worker dying halfway through the job.

## Start with the promise behind Cancel

Consider an export that waits for a recording interval, renders a clip, stores the result, and notifies the requester. Some jobs finish quickly. Others wait for a camera to reconnect or compete for a limited pool of render workers.

What does cancellation promise?

It might mean stop scheduling new work and hide any later result. It might mean request that the renderer stop, accepting that an already running operation can finish. It probably cannot mean recall an email that has already been accepted by a mail service.

These are different contracts. Pick one before adding a `cancelled` flag.

For this example, use a modest contract: cancellation prevents new steps from being authorized after it is committed. Already authorized external operations may finish. Their results are recorded, but they cannot advance the cancelled export. The UI reports cancellation requested while external work is still draining.

That contract needs a shared decision point. A notification consumer reading a stale copy of `cancelled = false` cannot enforce it on its own.

One implementation is a transaction on the export record: check the current state and version, authorize the next step, and record its dispatch intent together. Cancellation uses the same concurrency control. Whichever transaction commits first determines whether the step was authorized. A dispatch worker can still check for cancellation before sending, but that extra check cannot make a remote call atomic with the database.

The race has a defined outcome now. It has not disappeared.

Applied to the opening failure, this contract changes the outcome: cancellation commits before rendering finishes, so the completion handler never authorizes the email. The render may still produce an artifact; the UI shows cancellation requested until outstanding work is reconciled.

If the renderer supports cancellation, record a durable cancel intent and deliver it using the known operation key or job ID. Retry an uncertain response and reconcile the renderer's eventual status. A database flag alone will not release its GPU. If cancellation is unsupported or arrives too late, suppress further steps and clean up the unused artifact after determining that no active worker still needs it.

## An offset cannot answer the customer's question

Suppose the export request was consumed at partition 7, offset 812. Later messages say the recording became available and rendering started. Those positions help track delivery. They do not directly tell support whether export `exp-42` is waiting, stuck, cancelled, or safe to retry.

The application needs a current view with enough information to make its next decision. For this example, I would expect something like:

```text
export_id           exp-42
state               rendering
state_version       9
workflow_version    2
cancelled_at        null
deadline            2026-10-16T18:00:00Z
render_operation    exp-42/render/<input-digest>
renderer_job_id     job-781
next_attempt_at     null
last_error          null
```

The input digest identifies an immutable specification: source recording version, interval, and render settings. The workflow version identifies the behavior governing this export. The state version supports concurrency checks. They serve different purposes; using one counter for all three makes recovery harder to reason about.

This view can live in a database or be maintained through stream processing. [Kafka Streams supports stateful processing and exactly-once processing guarantees](https://kafka.apache.org/41/streams/core-concepts/) when configured appropriately. It would be misleading to describe Kafka as incapable of maintaining application state.

The design question is who owns that state, how it is restored, and which operations are atomic with it. Reconstructing a history from events can be valid. It still requires decisions about event retention, schema evolution, and how old events map to today's code.

## The lost response is where retries become business logic

The render consumer sends a request. The renderer accepts it and creates `job-781`. Before the response reaches the consumer, the connection fails.

The consumer sees a timeout. The renderer sees a running job. Retrying with a new operation ID can start a second render. I covered the general lost-response problem in [AI Agents Are Distributed Systems](https://medium.com/@hamuryen/ai-agents-are-distributed-systems-treat-them-like-one-c4fcd0455708). Here the additional requirement is preserving one step's identity across the lifetime of an export, including cancellation and later recovery.

Kafka's [delivery semantics and transaction model](https://kafka.apache.org/41/design/design/) describe the guarantees available inside its processing boundary. A Kafka transaction does not automatically include a remote renderer or an email provider. Exactly-once processing within Kafka is valuable; the external effect still needs its own agreement.

First, the export request itself needs a client-supplied idempotency key, scoped to its customer, so resubmitting the same request returns the same export ID. Reject conflicting input for that key. Then define each step's operation identity before dispatch:

```text
operation_key = export_id + step_name + digest(immutable_step_input)
```

Retries of the same logical step reuse this key. A deliberate new export receives a new export ID. A changed render specification needs a new logical operation, not silent reuse of the old key.

The renderer must atomically associate that key with one job and return the existing job for repeated requests. It must also reject the same key with conflicting input. A client-side lookup followed by an ordinary create call is insufficient: two callers can both observe no job and both create one.

Key retention matters too. If the renderer forgets its deduplication record after an hour while consumers can replay a week-old request, the supposed guarantee ends after an hour. Keep the identity for the retry and recovery horizon, or reject operations whose safe retry window has expired.

Without cooperation from the renderer, an ambiguous timeout may need reconciliation or operator intervention. Changing the message broker cannot tell you whether that external operation happened.

## A database state machine is a serious middle option

Before adding a workflow platform, I would examine whether a small explicit state machine is enough.

For each incoming event, a database transaction can record the event ID in an inbox, validate the transition, update the export, and insert any outgoing intent into an outbox. A unique inbox key prevents the same delivered event from applying the transition twice. Commit the Kafka offset only after that durable handoff.

If the database commits and the offset commit fails, redelivery finds the inbox entry and does no additional work. If processing is concurrent, commit only the contiguous completed range for each partition; acknowledging a later record must not skip an earlier unfinished one.

An outbox relay publishes the recorded intent. It can publish twice if it crashes between publishing and recording progress, so recipients still deduplicate. Debezium's [outbox event router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html) documents one way to represent and route these records, including event identity and aggregate keys. The pattern closes the database-update/publication gap; it does not make every downstream effect unique.

Once accepted, work belongs to the durable job record. Do not keep the consumer waiting for a two-hour render to finish. A separate worker dispatches it, records the remote job identity, and reconciles completion. An expired worker lease can permit takeover, but does not prove the old worker stopped. Version checks and the external operation key still matter.

For database updates, make the check and update atomic: accept a transition only if the stored state version still matches the worker's expected version, then increment it. Fencing stale external writes requires the external service to enforce a monotonically increasing token as well. An idempotency key deduplicates the same operation; it does not by itself reject every command from a superseded worker.

Within one topic, a stable partitioning scheme can keep an export's records in the same partition and therefore in log order. Records in different topics have no shared Kafka ordering guarantee, even when they use the same export ID as their key. Neither arrangement makes asynchronously executed work finish in order. Conversely, one slow render only blocks unrelated records if the processing design waits synchronously or otherwise serializes them behind it. Kafka is not forcing that choice.

The workflow code now has explicit answers for failure cases:

| Event | Decision |
|---|---|
| Duplicate request | Return the existing export; do not create another logical job. |
| Render dispatch times out | Reconcile or retry using the same operation key. |
| Completion arrives after cancellation | Record the external outcome; do not authorize notification. |
| Old completion arrives after a replacement operation | Match the operation identity; do not advance the current step. |
| Deadline passes while waiting for a worker | Persist expiry and stop authorizing new work. |
| Worker dies after taking a lease | Recover the job after lease expiry, preserving step identity. |

The inbox catches duplicate delivery. Operation identity and state checks catch different events that are no longer relevant. Both are necessary.

## Waiting is part of the persisted state

“Retry in ten minutes” creates an obligation that outlives the process holding the timer.

In a database implementation, persist `next_attempt_at` and let a scheduler claim due work. Check the deadline again when dispatching; the queue may have delayed a job beyond its useful lifetime. Record why a retry is scheduled and whether a human can resume it. A dead-letter topic alone is not an answer to those questions.

Avoid treating all waits as failures. Waiting for footage to become available is expected progress. Repeated authorization failures at a storage service are not. A transient network timeout, missing recording interval, and invalid export specification need different retry policies.

There is also a product decision hidden in “deadline.” Does it mean no new work after that time, or no result should become visible afterward? A render already running at expiry can still produce a file. Under a no-new-work policy, an already authorized step may finish, while later steps remain blocked. Under a no-visible-result policy, the publication path must also check expiry before making the artifact available; delaying the scheduler's expiry event must not extend the deadline.

Neither rule erases compute already consumed. Record that cost and the eventual artifact outcome even if the customer-facing export ends as expired. Schedule cleanup separately and make it repeatable. Otherwise a workflow that looks terminal in the UI can leave storage and render jobs behind indefinitely.

These details are manageable for a small workflow. They become a substantial subsystem when every product flow has different branches, waiting conditions, and recovery actions.

## Where a workflow engine earns its place

A workflow engine becomes attractive when the team is repeatedly implementing durable waits, execution history, retries, and resumption across many flows. [Temporal's workflow execution model](https://docs.temporal.io/workflow-execution) is one example: it provides durable execution through recorded history and replay, rather than requiring the application to assemble those mechanics around every consumer.

It does not make the renderer's lost-response problem disappear. Temporal's [Activity documentation](https://docs.temporal.io/activity-definition) explicitly explains why Activities need idempotency: an external action may finish while its completion is never reported. Retrying that Activity still needs the same business operation identity.

Adopting an engine also brings deployment and versioning obligations. A workflow waiting for days may resume under changed code. A database state machine needs a migration policy for those old jobs; a replay-based engine needs changes compatible with its execution rules. Include that work in the decision.

Kafka can continue carrying facts that multiple independent systems need: a recording became available, an export was requested, an artifact was produced. The workflow owner decides what should happen next for a particular export. Those responsibilities can coexist.

For a straightforward consume-transform-produce pipeline, Kafka's processing model may cover the requirement well. For a few short business flows, an explicit database state machine may be sufficient. When their recovery machinery starts dominating feature work, a workflow platform deserves a serious evaluation.

I would make the choice by taking one cancelled export and asking the system to explain it: what was authorized, which external work may still be running, what will happen if the worker restarts, and whether a replay can send the email again. If answering requires reading five consumers and interviewing whoever last repaired the database, the workflow already exists. Its owner and rules are just difficult to find.

---

*I'm Burak Hamuryen, a software engineer in Berlin working on distributed systems and real-time video infrastructure. More at [hamuryen.com](https://hamuryen.com).*
