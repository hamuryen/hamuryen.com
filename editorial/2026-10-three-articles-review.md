# October 2026 article research and review record

Internal editorial notes. The three publication drafts are in `drafts/`; this file is not article copy.

## Scope and publication order

Prepared October 9, 2026. Suggested slots: October 12 (Python), October 14 (self-hosting), October 16 (Kafka). No publication or scheduling has been performed.

The author's supplied Medium screenshots are a small lifetime snapshot, with articles of different ages and languages. Views/presentations is not a defensible feed click-through rate; reads is not proof of completion. Topic selection uses readership signals cautiously, alongside current discussions and the author's established backend, distributed-systems, native-code, GPU/video, on-premise and edge experience. No traffic forecast is promised.

Python has a release-day hook; self-hosting has an active cost/quality argument and a reusable calculator; Kafka targets working backend engineers with a cancellation scenario. The Kafka article goes beyond the earlier AI-agents essay by centering authorization of steps, deadlines, durable handoff, and ownership of workflow state.

## Evidence boundaries

- Python's release date, syntax and upstream performance claims were checked against the final 3.15 documentation and PEP 810. Context7 was also consulted; versioned official documentation controls where indexed main-branch material could differ.
- The import experiment is original work prepared for the article. It is not represented as the author's historical production experience, a web-service benchmark, a JIT benchmark, or a comparison with 3.14.
- Self-hosting rates, hardware cost, throughput and power are explicitly illustrative. No vendor quote, GPU measurement, quality equivalence or current provider price is implied. All dollar amounts are USD.
- The Kafka export is a hypothetical design example, not a reported employer incident or a tested deployment. No Kafka/Temporal integration test is claimed.
- Reddit discussions supply questions worth examining, not proof of technical claims or market-wide prevalence. Relative timestamps in retrieved Reddit pages were inconsistent; no vote count or exact thread date is asserted in the articles.

## Primary sources

Python:

- https://www.python.org/downloads/release/python-3150/
- https://docs.python.org/3.15/whatsnew/3.15.html#upgraded-experimental-jit-compiler
- https://peps.python.org/pep-0810/
- https://docs.python.org/3.15/howto/free-threading-python.html

Cost and serving:

- https://aws.amazon.com/bedrock/pricing/ (billing dimensions only; no rates copied)
- https://huggingface.co/blog/tngtech/llm-performance-prefill-decode-concurrent-requests (TNG's own serving measurements; no performance number transferred to our hypothetical machine)
- https://docs.vllm.ai/en/latest/usage/metrics/
- https://www.reddit.com/r/LocalLLaMA/comments/1ww2jsu/selfhosting_ai_does_not_save_money_and_i_do_it/

Workflow design:

- https://kafka.apache.org/41/design/design/
- https://kafka.apache.org/41/streams/core-concepts/
- https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html
- https://docs.temporal.io/workflow-execution
- https://docs.temporal.io/activity-definition
- https://www.reddit.com/r/apachekafka/comments/1w6gv9m/we_used_kafka_as_workflow_execution_engine/

## Claude concept review and decisions

Claude was invoked through its local CLI, with tools disabled, strict empty MCP configuration, and no session persistence. The reviewer received article concepts, then the full drafts and both scripts. No credentials or private project material were supplied.

Accepted from the concept review:

- Avoid comparing a source-built 3.15 with an optimized packaged 3.14. Measure eager versus lazy on the same final 3.15 interpreter instead.
- Separate readiness, first useful call and second call; report medians, interquartile ranges, warmup and cache conditions.
- Make quality parity, maintenance time and API pricing visible in the cost decision. Include API-price sensitivity.
- Lead Kafka with cancellation and deadlines. Define stable external operation identity and a specific cancellation contract.

Disagreements sent back to Claude:

- Charging idle power for 730 hours plus only the active-minus-idle increment is correct; it does not double-charge idle power.
- The cost example includes ongoing operations (2 hours at $75/hour); it does not assume free labor.
- A long external render does not inherently block a Kafka partition. Synchronous waiting or equivalent serialization would cause that blocking.
- Lookup by an external operation key is insufficient by itself; creation/deduplication must be atomic at the external service.

## Executed verification

Final CPython 3.15.0 was built from the official release archive, with Clang 21.0.0 on macOS ARM64 and configure flags `--without-ensurepip --disable-test-modules`. The raw result records GIL enabled and no JIT. An earlier downloaded release candidate was not used for the reported results.

The import experiment completed 5 discarded warmups and 60 retained fresh-process observations per case. A separate check recomputed all summary medians from the 120 observations and verified eager/lazy module-loading assertions. This is one local run with warmed filesystem caches and no thermal/frequency control; no significance claim is made for the small difference in total time.

The cost calculator's model checks passed, including equality at break-even, full-load energy without double-counting idle power, no crossover for zero API price, increased operations cost, and rejection of demand beyond idealized capacity. Six-hour operations and half/double API-rate scenarios were executed separately. All local article links resolved.

Codex Security's preflight initially failed under system Python 3.9 because `tomllib`/`tomli` was unavailable; rerunning that helper under 3.15 passed. The scan MCP itself still launched with its own incompatible Python environment and failed on the same missing dependency before producing a scan identity. Therefore no completed Codex Security scan is claimed. The two scripts remain local CLI examples, and their source was also supplied to Claude for review. No user configuration or system Python installation was changed to repair the optional scanner.

## Full-draft review and revisions

Claude explicitly conceded the four concept-stage disagreements above and verified the cost arithmetic. It identified title/claim alignment, cancellation follow-through, request identity, and excessive generic sections as useful improvements.

Changes made:

- Retitled Python to **Python 3.15 Lazy Imports: Where the Startup Cost Goes**, avoiding a promise of a 3.14-to-3.15 backend benchmark. Condensed generic free-threading/checklist material. Explained the eager first-call overhead without inventing its cause. Separated hypothetical 20% arithmetic from upstream JIT numbers.
- Verified the final interpreter's import flag and dotted lazy import through execution as well as documentation. Confirmed `clang --version` reports **Apple Clang 21.0.0**, despite the reviewer's initial doubt. Disclosed the small membership-check overhead in the first-call timing window.
- Required a final 3.15 interpreter in the runner, improved failed-semantics diagnostics, made JIT metadata optional, and clarified calculator `--check` help.
- Added multi-host cost steps, resale-value effects, and explicit rejection of monthly-average feasibility as a sufficient test.
- Closed Kafka's opening scenario, added durable remote cancellation and eventual cleanup, established customer-scoped request idempotency, added `cancelled_at`, linked the prior AI-agents essay, and expanded deadline/visibility semantics.

Rejected and sent back with reasoning:

- A default 30% utilization multiplier is not evidence that a bursty service is feasible. The example deliberately demonstrates that 500,000 requests can fit a month's theoretical ceiling while failing a 44-hour arrival window. Keeping an explicitly necessary-only ceiling is more honest than inventing a universal safe utilization.
- Moving the `loaded_at_ready` observation after first use destroys the observation it is intended to make. Kept it before first use and disclosed instrumentation cost.
- Did not relabel the hypothetical electricity rate as an actual Berlin tariff or silently change the hypothetical JIT arithmetic to an upstream estimate.

The revised runner completed another 120 retained observations. Combined-time medians in that verification run were 30.175 ms eager and 30.117 ms lazy, consistent with the article's narrow interpretation. The article and committed raw data retain the original run rather than selecting the most favorable result.

## Final Claude review

The third review (concept, full draft, revised draft) accepted the capacity reasoning and remaining technical corrections. Claude considered the self-hosting article publishable and the other two publishable after link checks and a reproduction-time wording fix.

The Kafka 4.1 URLs were retrieved successfully from the official site, including the unusual but valid `/41/design/design/` path. The prior-essay link was changed to the published essay's Medium URL found in `index.html`. Web retrieval followed its redirect to the author's custom domain but could not retrieve that page; the destination's current response was not independently verified. Removed the unnecessary promise that the benchmark takes only a few seconds. Added the 44-hour capacity counterexample to the calculator's checks.

The companion links resolve in the draft tree, and `scripts/package-site.py` copies that tree intact. They are not yet deployed. When transferring these articles to Medium, deploy the companion files and use absolute URLs under `https://hamuryen.com/drafts/examples/` (or attach equivalent downloadable files); a Medium article cannot retain repository-relative links. This is a publication step, not a completed deployment claim. Do not publish the Python or cost article without accessible companion materials.

## Additional independent Codex and Claude reviews

At the author's explicit request, both reviewers assessed the finished drafts afresh. The Codex reviewer was instructed not to read the prior reviews before forming its judgment. The new Claude call received the articles, companion scripts and measured summary without earlier verdicts. Claude had no browsing tools; independent official-source checks were performed by Codex. These are editorial/technical reviews, not completed Codex Security scans.

### Independent Codex findings

Two medium-priority ambiguities were identified and fixed:

1. **Kafka ordering:** using the same export key across multiple topics does not provide a combined order. The text now specifies one topic, stable partitioning, and ordering within that partition, separately from asynchronous completion.
2. **Cost scope:** the local table included operations while the API expression contained token charges alone. The two hours are now explicitly additional local operations relative to the API option, the $20 is local-specific overhead, and shared application costs are omitted from both sides. The calculator docstring uses the same definition.

The reviewer independently recomputed the archived medians and quartiles, verified interval sums, ran the calculator checks, checked official Python/Kafka/Temporal documentation and TNG's serving analysis, and reran the full import experiment. Its separate run yielded eager readiness 30.028 ms, eager first-result total 34.514 ms, lazy readiness 0.000792 ms, and lazy first-result total 34.454 ms. Host timing varied, but the cost-shift conclusion reproduced. No production Kafka deployment, LLM benchmark, traffic forecast or biographical verification was performed.

### New Claude findings and adjudication

Accepted useful criticism:

- The Python lead overemphasized a sub-microsecond measurement close to instrumentation cost. Replaced it with the robust observation that roughly 26 ms moves past readiness.
- Made the eager first-use finding a separate section and investigated it. A new `-X importtime` run shows `email.message`, `email._encoded_words`, and `email.iterators` loading on first parse. The final 3.15 source's default-policy `FeedParser` constructor imports `Message` inside the function. Saved the trace beside the benchmark and clearly separated diagnostic timings from the original measurements.
- Added cost sensitivity at 0.2, 1 and 3 assumed requests/second, holding power fixed and explicitly retaining hypothetical-capacity status.
- Clarified that the cancellation contract changes the opening failure's outcome. Explained atomic database version checks and externally enforced fencing, distinguishing these from operation deduplication.
- Removed some repetitive conditional and contrastive phrasing while retaining necessary evidence limits.

Rejected incorrect suggestions, with the reasoning sent back to Claude:

- The API/local incremental-unit-cost ratio is 144, not four orders of magnitude. The baseline approximation `F/a` being close does not make capacity or electricity universally irrelevant; idle electricity is already in `F`, and throughput can invalidate service feasibility.
- Adding API-specific operating cost increases the local option's advantage. It cannot reverse a six-dollar local advantage in favor of the API. Defining differential operations resolves the real ambiguity without inventing a new cost estimate.
- A roughly 0.1 ms difference between the observed total-time medians does not establish a meaningful improvement. The lead does not make that claim.
- Testing one clearly bounded module establishes this mechanism, not its prevalence. Retained that limit instead of presenting a few extra modules as representative application evidence.

### Codex review of the revisions

The independent reviewer confirmed both original findings were resolved, recomputed every new sensitivity row, and checked the new import trace against the final 3.15 source. It also verified the cancellation/fencing changes and agreed with the three numerical/inference corrections above. Its final delta verdict: **no further blocking findings**, with production-integration and traffic-validation limits unchanged.

### Claude reconciliation

Claude received the revised sections and the numerical objections, conceded the ratio/API-overhead/shortcut errors, rechecked the arithmetic, and reported **no substantive blocker remaining in the reviewed excerpts**. It agreed that the single-module scope should remain bounded and that database version checks and externally enforced fencing are different guarantees. Its two final small suggestions were applied: explicitly state milliseconds for the second parse, and say both fixed costs and power are held constant in the throughput sensitivity table. Claude's final pass covered the revised excerpts, not a new independent execution or another full-manuscript review.


## Cover artwork and cleanup

Generated with the built-in image_gen tool; selected PNGs were copied into drafts/assets and visually inspected. The covers are editorial metaphors rather than measured diagrams. No image text or logos were added. Each draft includes descriptive alt text, and blog-ideas.md links its cover.

- Python: python315-lazy-imports-cover.png, 1659 × 948. One targeted correction made the amber block counts equal (five in each row).
- Costs: self-hosting-ai-cost-cover.png, 1672 × 941. A near-level scale avoids declaring either hosting option universally cheaper.
- Kafka: kafka-workflow-engine-cover.png, 1672 × 941. The stopped branch and continuing branch represent deliberate workflow control.

Removed 27 task-generated temporary files/directories (423.3 MiB logical size), including browser research logs, temporary review exchanges, downloaded Python runtimes, build tree/archive and cache. Kept the three drafts, final cover assets, runnable companion scripts, primary raw observations, import trace and this consolidated research record. Temporary paths mentioned in earlier review evidence are historical and have been cleaned up.

### Generation prompt set

**python**

```text
Use case: stylized-concept. Create one beautiful editorial cover image for a serious software engineering essay: "Python 3.15 Lazy Imports: Where the Startup Cost Goes". No text in the image. Wide landscape 16:9, ideally 1792x1024 or wider, safe central composition for Medium thumbnail crops. A meticulously made miniature mechanical experiment photographed in a premium industrial design studio: two parallel brushed-aluminum tracks on a warm off-white surface, each carrying the SAME amount of translucent amber glass blocks. On the upper track the amber blocks are stacked before a thin blue glass gateway near the beginning; on the lower track those same blocks are stacked just after a matching gateway further along. The visually unmistakable metaphor is that the work has moved to a later point rather than disappeared; identical work volume in both tracks. Restrained cobalt blue and amber accents, warm neutral backdrop, soft daylight, realistic material imperfections, elegant generous space, strong readable silhouettes, editorial still-life photography / restrained high-end 3D art direction. Interesting oblique overhead perspective, crisp focal subjects, subtle shadows. No snakes, no Python logo, no lettering, no numbers, no code, no arrows, no charts, no futuristic glowing neon, no robot heads, no watermarks. One coherent art-directed scene, not a collage. Think a meaningful magazine illustration with the tactile finish of a photographed physical model.
```

**cost**

```text
Use case: stylized-concept. Create one beautiful editorial cover image for a serious engineering essay: "When Is Self-Hosting AI Actually Cheaper?" No text in image. Wide landscape 16:9, safe centered composition for thumbnail crops. A precise brushed-aluminum balance scale photographed as a premium editorial still life on a warm off-white studio surface. On one pan sits one small realistic compact GPU server, silver enclosure, dark fan grille, a few warm amber glass blocks beside it representing fixed operating cost. On the other pan sits a simple sculptural translucent cobalt-blue cloud containing small identical amber glass tokens, representing pay-per-use cloud compute. The beam is nearly level, conveying a decision depending on workload, with neither option declared the winner. Mechanically believable scale and two clearly separate pans. Keep the server recognizable and the cloud elegant rather than cartoonish. Restrained cobalt, amber and silver palette, physically realistic metal and frosted glass, soft side daylight, subtle contact shadows, clean negative space, exceptional editorial object photography feel. No coins with dollar signs, no financial numbers, no typography, no labels, no logos, no robot brains, no circuitry background, no neon gradients, no watermarks. One concise meaningful metaphor, polished high-quality landscape magazine cover.
```

**kafka**

```text
Use case: stylized-concept. Create one beautiful editorial cover for a technical essay "Your Kafka Consumers Are Becoming a Workflow Engine". No text in image. Wide landscape 16:9, centered safe composition for article thumbnail crops. A sophisticated tabletop mechanical workflow model, photographed at oblique overhead angle on warm off-white background: brushed-aluminum tracks connect three distinct stations, carrying upright small translucent cobalt-blue rectangular job cards with subtle film-frame perforations suggesting video exports. The path branches at a deliberate junction. One branch ends at a clearly CLOSED matte burnt-orange stop gate in the foreground, with one blue job card waiting safely before it. Another branch remains open and continues toward a neat stack of finished cards. A few minimal connected hubs and a small physical timing dial with no numerals suggest coordinated steps, deadlines and cancellation. Visually clear separation between a closed cancelled path and still running independent work. The story is deliberate control over a workflow, not a catastrophic collision or broken machinery. Elegant restrained industrial miniature, tactile silver metal, frosted glass, warm amber/orange and cobalt, soft daylight, realistic shadows, beautiful editorial photography style consistent with an engineering publication. Uncluttered and readable at small size. No text, no letters, no Kafka logo, no code, no numerical labels, no generic glowing network, no robot heads, no watermarks. One cohesive physical scene, not a UI screenshot or schematic.
```

Python final edit instruction: Preserve the scene, camera angle, lighting and materials. Change only the foreground row from six amber cubes to exactly five, matching the five cubes in the background row. Keep the foreground cubes after its blue gate and the background cubes before theirs.



## Medium publication — verified October 9, 2026

- Python 3.15 Lazy Imports: Where the Startup Cost Goes: scheduled 2026-10-10T10:00:00+02:00 (Europe/Berlin). [Edit](https://medium.com/p/966c2b3f3b41/edit).
- When Is Self-Hosting AI Actually Cheaper?: scheduled 2026-10-12T10:00:00+02:00 (Europe/Berlin). [Edit](https://medium.com/p/5339fec9b579/edit).
- Your Kafka Consumers Are Becoming a Workflow Engine: scheduled 2026-10-14T10:00:00+02:00 (Europe/Berlin). [Edit](https://medium.com/p/6e7f424baa3c/edit).

Native rich-text import preserves all source prose and code; Markdown tables are five readable PNG figures with captions and alternative text. Compared source HTML text against saved Medium article exports: no missing source text in any article. Cover and caption layouts inspected at 390px; Kafka desktop inspected as well. Topic lists and SEO title/description reloaded from settings; each scheduled time reopened and verified as 10:00 AM GMT+2. Scheduled calendar shows October 10, 12 and 14. The outbox list displayed 08:00, while the scheduling UI explicitly retained 10:00 GMT+2. Subscriber email notification disabled; no external promotion sent.

Python code-block merge attempt caused a save error; backed up local editor state and, after explicit user permission to refresh, restored the saved version. The first example remains two consecutive code blocks; source-text comparison confirms no loss. Custom-domain redirects initially returned a Cloudflare challenge, so verification used authenticated Medium editor/settings/calendar. No public-page rendering claim is made.

Supporting public Gists: [Python experiment](https://gist.github.com/hamuryen/b2a4dfc15af70d141043a76305497569), [AI cost calculator](https://gist.github.com/hamuryen/06345e4ca3dcff0216e4e9eb78e5214c). Final captions, alt text, five topics and SEO metadata are recorded in `drafts/medium/publication-manifest.json`.
