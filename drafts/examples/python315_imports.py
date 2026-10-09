"""Python 3.15 eager/lazy import experiment. Stdlib only; JSON to stdout.

Run with a final Python 3.15 interpreter. Each observation uses a fresh process.
The measured window excludes interpreter startup and JSON serialization.
Bytecode writes are disabled; existing stdlib bytecode and OS caches are left
alone. Warmup primes caches, so this is NOT a cold-filesystem measurement.
"""

import json
import platform
import random
import statistics
import subprocess
import sys
import sysconfig
from datetime import datetime, timezone


def main():
    if sys.version_info[:2] != (3, 15) or sys.version_info.releaselevel != "final":
        raise SystemExit("Use a final Python 3.15 release for both cases.")
    template = '''
import sys
from time import perf_counter_ns
assert "email.parser" not in sys.modules, "Parser was already imported before timing"
start = perf_counter_ns()
{declaration}
ready = perf_counter_ns()
loaded_at_ready = "email.parser" in sys.modules
first = email.parser.Parser().parsestr("Subject: Example\\n\\nBody")
used_once = perf_counter_ns()
second = email.parser.Parser().parsestr("Subject: Example\\n\\nBody")
used_twice = perf_counter_ns()
assert first["Subject"] == second["Subject"] == "Example"
import json
print(json.dumps(dict(
    ready_ms=(ready-start)/1e6,
    first_call_ms=(used_once-ready)/1e6,
    second_call_ms=(used_twice-used_once)/1e6,
    ready_plus_first_ms=(used_once-start)/1e6,
    loaded_at_ready=loaded_at_ready,
)))
'''
    declarations = {"eager": "import email.parser", "lazy": "lazy import email.parser"}

    def run(case):
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-X", "lazy_imports=normal", "-c",
             template.format(declaration=declarations[case])],
            capture_output=True, text=True, check=True, timeout=30,
        )
        data = json.loads(result.stdout)
        if data["loaded_at_ready"] != (case == "eager"):
            raise RuntimeError(f"{case}: import timing semantics check failed")
        return data

    for _ in range(5):
        for case in declarations:
            run(case)
    order = [case for case in declarations for _ in range(60)]
    random.Random(315).shuffle(order)
    samples = {case: [] for case in declarations}
    for case in order:
        samples[case].append(run(case))
    summary = {}
    for case, observations in samples.items():
        summary[case] = {}
        for metric in ("ready_ms", "first_call_ms", "second_call_ms", "ready_plus_first_ms"):
            values = [sample[metric] for sample in observations]
            q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
            summary[case][metric] = dict(median=statistics.median(values), q1=q1, q3=q3)
    jit = getattr(sys, "_jit", None)
    print(json.dumps(dict(
        measured_at_utc=datetime.now(timezone.utc).isoformat(),
        runtime=sys.version,
        platform=dict(system=platform.system(), release=platform.release(), machine=platform.machine()),
        build=dict(compiler=platform.python_compiler(),
                   configure=sysconfig.get_config_var("CONFIG_ARGS"),
                   gil_enabled=sys._is_gil_enabled(),
                   jit_available=jit.is_available() if jit else None,
                   jit_enabled=jit.is_enabled() if jit else None),
        trials_per_case=60, discarded_warmups_per_case=5,
        randomized_order=order, summary=summary, samples=samples,
    ), indent=2))


if __name__ == "__main__":
    main()
