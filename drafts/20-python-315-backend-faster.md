# Python 3.15 Lazy Imports: Where the Startup Cost Goes

*A small lazy-import experiment, and the measurements a release benchmark cannot make for you.*

![Five amber blocks sit before a blue gate on one track and after it on another, illustrating the same initialization work moving to a later stage.](assets/python315-lazy-imports-cover.png)

In a small experiment prepared for this article, changing one import to a lazy import moved roughly 26 milliseconds of work past a simulated readiness point.

The first useful operation still finished after about 30 milliseconds.

Both results are real. They describe different parts of the same process. That distinction matters when deciding what [Python 3.15, released on October 9](https://www.python.org/downloads/release/python-3150/), can do for a backend service.

The release includes work on the experimental JIT, free-threaded builds, and explicit lazy imports. These features affect different costs. A service can benefit from one and have little reason to use another. Before assigning an expected percentage improvement to an upgrade, I would want to know where the service spends its time and when that time is paid.

Lazy imports are the measured case here. JIT and free-threading appear later to explain why this result cannot stand in for an evaluation of the whole upgrade.

My perspective comes from backends that coordinate other systems, including native code and video infrastructure. In that setting, “Python is slow” is an incomplete diagnosis. It might mean Python code is consuming a core. It might mean a worker is waiting for storage. It might mean a process takes too long to become useful after deployment. Those need different experiments.

## Measure readiness and the first useful operation separately

[PEP 810](https://peps.python.org/pep-0810/) introduces explicit lazy imports. At module scope, this declaration defers loading until the imported name is used:

```python
lazy import email.parser

# Other startup work could happen here.
message = email.parser.Parser().parsestr("Subject: Example\n\nBody")
```

Ordinary imports retain their normal behavior under the default import mode. You choose which imports to defer. A module that is never used can avoid its initialization entirely; a module used immediately after readiness still has to load.

To examine that boundary, the [companion script](examples/python315_imports.py) runs eager and lazy versions in fresh processes using the same interpreter. Each process records four intervals:

1. From just before the import declaration to a synthetic “ready” marker immediately after it.
2. From that marker through the first parsed message.
3. The second parsed message.
4. The combined time through the first parsed message.

There is no web server in this experiment. “Ready” is a marker in a short script, not a successful HTTP health check. Interpreter startup and result serialization are outside the measured window.

The run used final CPython 3.15.0, built from the official source archive on macOS ARM64 with Apple Clang 21.0.0 from Xcode. The configure flags were `--without-ensurepip --disable-test-modules`; PGO and LTO were not enabled. The GIL was enabled and the build had no JIT. Five warmups per case were discarded, followed by 60 observations per case in a shuffled order.

| Interval | Eager import, median [Q1–Q3] | Lazy import, median [Q1–Q3] |
|---|---:|---:|
| Import declaration to ready | 26.158 [25.941–26.461] ms | 0.000709 [0.000698–0.000792] ms |
| Ready to first parsed message | 4.090 [4.046–4.156] ms | 30.196 [30.011–30.568] ms |
| Second parsed message | 0.0176 [0.0173–0.0192] ms | 0.0178 [0.0174–0.0190] ms |
| Start through first parsed message | 30.294 [29.995–30.548] ms | 30.197 [30.011–30.569] ms |

These are measurements from one local run on October 9, 2026. The Q1–Q3 ranges show the middle half of observations, not a confidence interval. The combined interval is measured directly; adding separate medians need not reproduce its median. The first-call window also includes a small `sys.modules` membership check that verifies whether the import had already happened at readiness.

The [raw observations and build metadata](examples/python315-import-results.json) accompany the script. Each child used isolated mode, disabled bytecode writes, and explicitly selected normal import mode. Existing standard-library bytecode was left in place, and warmups primed filesystem caches. This is a fresh-process experiment with warm caches, not a cold-disk test. CPU frequency, thermals, and background activity were not controlled. The sub-microsecond declaration timing is close enough to measurement overhead that I would only read it as negligible here.

The result supports a narrow conclusion: for this example, the lazy declaration shifts almost all of the import cost across the ready marker. It does not demonstrate a meaningful reduction in time to the first result, and it says nothing about HTTP throughput or Python 3.14 versus 3.15.

## Warm the path you intend to serve

Even with the eager import, the first parse takes roughly four milliseconds while the second takes about 0.018 milliseconds. There is still work left after importing the top-level parser.

A separate diagnostic run with `-X importtime` shows `email.message`, `email._encoded_words`, and `email.iterators` loading during the first parse. The [3.15 implementation of `FeedParser`](https://github.com/python/cpython/blob/v3.15.0/Lib/email/feedparser.py) explains why: with the default policy and no supplied message factory, its constructor imports `Message` inside the function. Eagerly importing `email.parser` does not execute that constructor.

You can inspect the same boundary without changing the benchmark:

```sh
python3.15 -I -B -X importtime -c 'import email.parser; print("BEFORE_FIRST_PARSE", file=__import__("sys").stderr); email.parser.Parser().parsestr("Subject: Example\n\nBody")'
```

Imports printed after the marker occur on first use. This diagnostic adds instrumentation, so its timings are separate from the table; it identifies deferred work without assigning every fraction of the original four milliseconds to an import. The [captured trace](examples/python315-first-use-import-trace.txt) accompanies the results.

For this dependency, “we imported it during startup” is an incomplete warmup check. Exercise the path the service actually needs. Other modules can behave differently; this single-module experiment establishes the mechanism, not its prevalence across an application.

## Decide who should pay for initialization

That shift can still be useful.

Imagine a command-line tool with a lightweight status command and a rarely used report command. Loading the report stack for `status` is unnecessary work. Deferring it can eliminate that cost for the entire invocation.

A backend has a more complicated choice. Suppose most requests use a lightweight route, while occasional requests generate reports. Deferring the report dependency can reduce startup work. The first report request then inherits the initialization cost. If many workers have just been replaced, many first requests may encounter it.

Whether that is acceptable depends on the service's contract. If reports are queued and complete asynchronously, a little extra initialization may be harmless. If the first report has the same latency deadline as every later one, warming that dependency before accepting report traffic may be the better policy.

Readiness should reflect the capability you intend to offer. A process returning `200 OK` from a trivial health endpoint does not establish that its critical request path can import its dependencies, load configuration, and perform the required work.

Lazy initialization also changes when failures and side effects occur. A missing dependency can fail at first use rather than startup. Registration code that runs during import does not run until the import is resolved. If a plugin registry depends on those side effects, deferring an import can change behavior, not just timing. That follows from the [semantics specified in PEP 810](https://peps.python.org/pep-0810/); test those paths before broadly changing import declarations.

Start with genuinely optional features, then make the warmup policy explicit for required capabilities. The service still needs to become ready to do what its callers expect.

## Read the JIT result with its denominator attached

The [3.15 release notes](https://docs.python.org/3.15/whatsnew/3.15.html#upgraded-experimental-jit-compiler) report geometric-mean gains on `pyperformance` of roughly 7–8% on x86-64 Linux and 11–12% on AArch64 macOS, against the respective optimized interpreter baselines. The macOS comparison uses the tail-calling interpreter. These are upstream results for the experimental JIT, not measurements of this article's example and not a promise that upgrading any 3.14 service yields those gains. The notes also report variation across individual benchmarks, including regressions.

A benchmark suite is useful evidence about the implementation. A backend response includes work outside that implementation.

Take a deliberately simplified request: 10 milliseconds executing Python code and 90 milliseconds waiting for a database. Choose a hypothetical 20% improvement in Python execution speed, unrelated to the upstream percentages above. That portion falls to about 8.33 milliseconds. The whole request falls from 100 to 98.33 milliseconds: about a 1.7% latency reduction.

That is arithmetic under fixed assumptions, not a service benchmark. It assumes serial work, unchanged database time, and no queueing. Near saturation, reducing CPU demand can also reduce waiting in a worker queue, so the end-to-end effect may be larger. Conversely, a new bottleneck can limit throughput. Measure at the concurrency that matters.

For a JIT evaluation, separate startup, warmup, and sustained execution. A short-lived job and a long-running worker provide different opportunities to recover compilation work. Include memory use and CPU per completed request alongside latency. A lower median that increases memory enough to reduce worker density might be an unattractive trade in a constrained deployment.

Compare equivalent builds: a 3.14-to-3.15 experiment needs matching optimization flags and the same machine and workload. A source build without PGO against an optimized distributor build changes more than the Python version.

## Free-threading needs a workload and dependency check

A free-threaded build addresses another question: can multiple Python threads execute the relevant work in parallel, and does that improve this application?

The [Python 3.15 free-threading guide](https://docs.python.org/3.15/howto/free-threading-python.html) explains both the build distinction and an important compatibility behavior: importing an extension that does not declare free-threading support can re-enable the GIL. Check the running process after loading the application's actual dependencies. Do not infer its state from the installer you selected.

The workload matters: Python computation, native libraries with their own thread pools, and network waits offer different opportunities. Shared state needs attention too. A cache can have thread-safe individual accesses while a check-then-initialize sequence still creates the same resource twice. Successful concurrent requests alone do not establish correctness.

Compare a fixed CPU and memory budget. An existing deployment may already use multiple worker processes to occupy several cores. The relevant result is useful work per allocated resource under the same latency requirement.

## A useful upgrade result fits on one page

For a real backend, keep readiness, first-use latency and steady-state behavior beside the compatibility results. Hold the workload and resources fixed and change one feature at a time. A version upgrade, JIT activation and a move to free-threading deserve separate comparisons.

To reproduce the lazy-import experiment with a final Python 3.15 interpreter:

```sh
python3.15 python315_imports.py > python315-import-results.json
```

Its most useful number is the pair of roughly 30-millisecond totals. Without them, the readiness improvement would sound much more impressive than the change experienced by the first caller.

For a rarely used command, avoiding the import could be the whole win. For a backend that needs the module on its first request, I would decide explicitly whether startup or the caller should pay. That is the sort of answer I want from an upgrade experiment: a measured change tied to a workload, with the displaced cost still visible.

---

*I'm Burak Hamuryen, a software engineer in Berlin working on distributed systems and real-time video infrastructure. More at [hamuryen.com](https://hamuryen.com).*
