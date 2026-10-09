# When Is Self-Hosting AI Actually Cheaper?

*A monthly cost model, and the workload assumptions that can make it useless.*

![A balance scale weighs a local GPU server against a blue cloud and usage tokens, illustrating the tradeoff between ownership and pay-per-use costs.](assets/self-hosting-ai-cost-cover.png)

At 100,000 requests a month, the local server in the example below costs $293.98. The API costs $300.

That looks like a win for self-hosting. Four more hours of maintenance turn the local bill into $593.98. No hardware changed. No model got slower. We simply charged for more of the work.

These are deliberately hypothetical numbers, not a quote for a particular GPU or model. I want to make the decision inspectable before arguing about the answer.

A recent [discussion about the cost of self-hosting AI](https://www.reddit.com/r/LocalLLaMA/comments/1ww2jsu/selfhosting_ai_does_not_save_money_and_i_do_it/) captures why these comparisons become heated. One person already owns the machine. Another is buying it for this purpose. Someone values keeping personal data at home more than the price difference. Someone else needs a model their hardware cannot run. They can all do the arithmetic correctly and reach different conclusions.

My background is in backend services, GPU video pipelines, and deployments spanning cloud, customer networks, and edge devices. The part of this question I recognize is capacity: what useful work does the machine deliver, under what conditions, and who keeps it working?

## Agree on what counts as a successful request

Before comparing prices, give both options the same job.

For a document extraction service, that could mean a defined mix of document lengths, required fields, an acceptable error rate, and a response deadline. For an interactive assistant, the time before the first token appears and the pauses during generation may matter as much as total completion time.

The same model and precision are a clean starting point when both providers offer them. Different models can still be compared, but then the comparison is between systems that meet the same application requirements. A cheaper answer that needs a second model to repair it belongs in the bill too.

This changes the denominator. Cost per generated token is useful for understanding a serving engine. Cost per accepted extraction, resolved request, or completed task is closer to what the application buys.

Keep rejected outputs, retries, and fallbacks in the numerator. If twenty percent of local results go to an external model for repair, the local system has an API bill. If the API needs retries, it should carry those costs as well.

For the worked example, assume every request completes successfully in one attempt on either system, with equivalent acceptable output. That is a simplifying assumption to replace with measured behavior, not a property of local or hosted models.

## A small model you can change

Use one request shape: 4,000 input tokens and 500 output tokens. Assume an API price of $0.50 per million input tokens and $2 per million output tokens. **These are illustrative rates, not current prices for a named provider.**

The API cost per request is:

```text
(4,000 × $0.50 + 500 × $2) / 1,000,000 = $0.003
```

Actual provider billing needs more care. For example, [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) distinguishes model-specific input and output rates, batch processing, and applicable cache pricing. Copy the billing rules for the service you would actually use; do not substitute the price of a consumer chat subscription.

Now give the local option an explicit budget. Compare costs that differ between the options: the two operations hours below are additional work for local hosting relative to the API, and the $20 covers local-specific recurring overhead. Shared application development and operations are omitted from both sides. The dollar totals are comparable incremental costs, not the entire application's operating budget.

| Assumption | Value |
|---|---:|
| Complete machine purchase | $3,600 |
| Cost spread across | 36 months, zero residual value |
| Powered-on time | 730 hours per month |
| Whole-machine idle power | 100 W |
| Whole-machine active power | 350 W |
| Electricity | $0.30/kWh |
| Additional local operations relative to API hosting | 2 hours per month at $75/hour |
| Other local-specific recurring costs | $20 per month |
| Effective active throughput | 1 accepted request/second |

That last row is particularly important. It is **an assumed capacity for this calculation**, not a claim that a $3,600 machine can serve this workload at that rate. The model has no named hardware, model weights, quantization, or benchmark behind it. If your chosen system cannot meet the quality and latency requirements, a favorable result from this table is irrelevant.

The monthly fixed cost is:

```text
Hardware:       $3,600 / 36                  = $100.00
Idle energy:    0.100 kW × 730 h × $0.30/kWh =  $21.90
Operations:     2 h × $75/h                 = $150.00
Other:                                       $20.00
Total:                                      $291.90
```

Idle electricity already covers the entire month. During active time, add only the extra 250 W, otherwise the idle portion gets charged twice.

At one request per second, the assumed incremental electricity cost is:

```text
(0.250 kW × $0.30/kWh) / 3,600 requests/h
    = $0.000020833 per request
```

The resulting monthly comparison is:

| Accepted requests | Local cost | API cost | Assumed active time |
|---|---:|---:|---:|
| 10,000 | $292.11 | $30.00 | 2.78 hours |
| 100,000 | $293.98 | $300.00 | 27.78 hours |
| 500,000 | $302.32 | $1,500.00 | 138.89 hours |

This is a single-host, steady-workload accounting case. It excludes initial integration effort, financing, taxes, unexpected repairs, cooling beyond the measured machine power, and redundancy. Production planning should add those costs to whichever side incurs them. It also assumes the API has enough quota to serve the workload without a separate capacity commitment.

The small [Python calculator accompanying this article](examples/ai_hosting_costs.py) reproduces the table. Every input can be changed:

```sh
python3 ai_hosting_costs.py --check
python3 ai_hosting_costs.py --ops-hours 6 --requests 100000
```

It requires only the standard library and makes no network requests.

## Find the assumption that changes the decision

Write local cost as `F + vN`, where `F` is monthly fixed cost, `v` is incremental cost per accepted request, and `N` is accepted requests per month. Write API cost as `aN`.

If `a > v`, the arithmetic break-even is:

```text
N = F / (a - v)
```

For the example, it is approximately 97,980 requests per month. If the API unit cost is no higher than the local variable cost, there is no volume at which this positive fixed cost gets recovered through cheaper requests.

This line only applies while one host can serve the workload. If the required arrival rate exceeds its sustainable capacity, adding another machine introduces another purchase, idle-power budget and potentially more operations work. Local cost then rises in steps. Extrapolating the first host's cheap incremental requests past that boundary understates the bill.

Zero resale value is also a deliberate assumption. An expected resale value reduces the hardware component to `(purchase − resale) / months`, moving break-even in favor of local hosting. Use a realistic estimate for the end of your ownership period, including the cost of selling or replacing the machine.

At 100,000 requests, the apparent advantage is about six dollars a month. That is too small to survive much uncertainty. Raising operations from two hours to six increases the fixed cost to $591.90 and moves break-even to roughly 198,680 requests.

The API rate has a similarly large effect. Holding the workload and local assumptions fixed, halving both token prices moves break-even to about 197,341 requests; doubling them brings it down to about 48,820. At 100,000 requests, active electricity contributes only $2.08 of the $293.98 local total. In this particular model, arguing over a few watts matters much less than choosing the right API comparison and accounting for engineering time.

Changing output length is more involved: it changes the API bill and the local service rate. Do not increase output tokens in the calculator while keeping throughput fixed unless a measurement supports that combination.

Changing only the assumed throughput illustrates a different sensitivity:

| Assumed requests/second | Break-even requests/month | Active hours for 100,000 requests |
|---|---:|---:|
| 0.2 | 100,800 | 138.89 |
| 1 | 97,980 | 27.78 |
| 3 | 97,526 | 9.26 |

The financial crossing point moves little, while required machine time changes fifteenfold. These are still hypothetical capacities with fixed costs and power held constant; buying different hardware would change those assumptions too. They show why a reassuring cost calculation can coexist with a service that cannot keep up.

The additional operations budget covers the difference in maintaining the serving stack, evaluating updates, investigating failures, and restoring service. Hosted APIs require engineering too; the example assumes that shared effort cancels. If your API option also has separate fixed charges, use the difference between the two fixed-cost totals in the break-even calculation rather than treating the API as free to operate.

For an existing workstation, the next decision may be much smaller: run tonight's job locally or pay an API. Purchase price can reasonably be sunk for that decision. It remains relevant when deciding to buy a replacement, reserve the machine for inference, or deploy another site. I would keep a marginal-cost calculation and an ownership-cost calculation beside each other rather than use one to answer both questions.

## Monthly volume can hide an impossible service

The table's 500,000 requests use about 139 active hours at the assumed rate. Spread over a month, that sounds comfortable.

Suppose most arrive during a two-hour window each weekday. With 22 working days, they now have 44 hours in which to run. The average arrival rate inside those windows is about 3.16 requests per second, before accounting for bursts. A machine sustaining one request per second cannot keep up during that period.

For an overnight batch, a backlog may be fine. For a live assistant, it may violate the response deadline. An hourly cost calculation cannot decide that distinction for you.

Batching also complicates the assumed service rate. TNG's [analysis of concurrent LLM serving](https://huggingface.co/blog/tngtech/llm-performance-prefill-decode-concurrent-requests) describes how admitting prompt-processing work can interfere with ongoing token generation. A higher aggregate token rate can coexist with a less responsive individual session. Use the throughput that meets your latency requirement, not the highest number printed by a benchmark.

In a trial, replay the arrival pattern and prompt-length distribution you expect to serve. Include long inputs, cancellations, and cache misses. Report queueing and the slower responses, not just an average from requests issued one at a time. [vLLM exposes separate metrics](https://docs.vllm.ai/en/latest/usage/metrics/) for queue time, time to first token, token-generation latency, and end-to-end request time; those distinctions are useful even with another server.

The calculator rejects demand above the physical ceiling of its assumed rate multiplied by powered-on hours. Passing is only a necessary condition, never a feasibility verdict. Even the 500,000-request example passes that check and fails the 44-hour service window. A blanket utilization allowance cannot fix this: capacity planning needs the arrival pattern, tolerated backlog, maintenance windows and response deadline together.

## Availability changes the bill before the first outage

A single workstation and a managed endpoint may satisfy very different service expectations.

If maintenance can wait until morning, one local machine may be sufficient. If a customer workflow must continue through a machine failure, account for spare capacity, recovery time, and the person responsible for using it. An API fallback may be cheaper than a second local host, but only if sending the data there is permitted and the application accepts its output.

An API is not an unlimited backup generator. Check quotas and the failure behavior of your client. The worst time to discover an insufficient rate limit is when every local request moves to the fallback at once.

For a fleet of customer installations, repeat this calculation per site. A hundred underused devices do not become one well-utilized device because their totals look healthy on a dashboard. Capacity can only be shared where data movement, network access, and response requirements allow it.

That is where my experience with on-premise and edge systems shapes the question. A locally processed workload might be worth paying more for because it must continue without a WAN connection or keep data inside a customer's network. Evaluate that requirement separately from token cost.

## What I would need before buying the machine

I would want a workload sample with an acceptance test, a measured service rate under its latency limit, and a monthly arrival profile. Then I would run the cost model across plausible values for maintenance time, electricity, API pricing, and hardware lifetime.

If the answer changes after adding four hours of work, I would treat that as a close decision. If it stays favorable across the realistic range, the hardware proposal has a stronger basis.

For the worked example, I would not buy a machine on the strength of a six-dollar monthly saving. I would first replace the assumed service rate with a measurement, price the necessary availability, and check whether the result survives a less favorable maintenance month. Those changes could settle the decision before any argument about which deployment model is inherently cheaper.

---

*I'm Burak Hamuryen, a software engineer in Berlin working on distributed systems and real-time video infrastructure. More at [hamuryen.com](https://hamuryen.com).*
