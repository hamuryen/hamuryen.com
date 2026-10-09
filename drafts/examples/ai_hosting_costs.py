"""Illustrative single-host cost model, not a hardware benchmark or vendor quote.

Python 3.9+. Run with --help to replace every assumption. USD throughout.
Operations hours and other overhead are additional local costs relative to the
API option; shared application costs are omitted from both sides. The model
does not represent separate API fixed charges.
Capacity means accepted requests per second at the required quality and latency.
It is an assumed input here; measure it for your own workload before buying.
"""

import argparse
from dataclasses import dataclass, replace
import math


@dataclass(frozen=True)
class Assumptions:
    hardware: float = 3600
    months: float = 36
    hours: float = 730
    idle_watts: float = 100
    active_watts: float = 350
    electricity: float = 0.30
    ops_hours: float = 2
    ops_rate: float = 75
    other: float = 20
    requests_per_second: float = 1
    input_tokens: float = 4000
    output_tokens: float = 500
    input_price: float = 0.50
    output_price: float = 2

    def validate(self):
        for key, value in vars(self).items():
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{key} must be finite and nonnegative")
        if min(self.months, self.hours, self.requests_per_second) <= 0:
            raise ValueError("months, hours and requests_per_second must be positive")
        if self.active_watts < self.idle_watts:
            raise ValueError("active_watts must be at least idle_watts")

    @property
    def fixed(self):
        return (self.hardware / self.months
                + self.idle_watts / 1000 * self.hours * self.electricity
                + self.ops_hours * self.ops_rate + self.other)

    @property
    def variable(self):
        return ((self.active_watts - self.idle_watts) / 1000
                * self.electricity / (self.requests_per_second * 3600))

    @property
    def api(self):
        return (self.input_tokens * self.input_price
                + self.output_tokens * self.output_price) / 1_000_000

    @property
    def capacity(self):
        return self.hours * 3600 * self.requests_per_second

    @property
    def break_even(self):
        saving = self.api - self.variable
        return self.fixed / saving if saving > 0 else None

    def compare(self, requests):
        if not math.isfinite(requests) or requests < 0:
            raise ValueError("requests must be finite and nonnegative")
        if requests > self.capacity:
            raise ValueError("demand exceeds even the idealized monthly capacity")
        return self.fixed + requests * self.variable, requests * self.api


def check_model():
    case = Assumptions()
    case.validate()
    assert math.isclose(case.fixed, 291.90)
    assert math.isclose(case.api, 0.003)
    local, api = case.compare(case.break_even)
    assert math.isclose(local, api)
    # Full utilization pays the full active power, with no double-counted idle power.
    full, _ = case.compare(case.capacity)
    expected = 100 + 0.350 * 730 * 0.30 + 150 + 20
    assert math.isclose(full, expected)
    assert replace(case, input_price=0, output_price=0).break_even is None
    assert replace(case, ops_hours=6).break_even > case.break_even
    # Monthly volume fits, yet the article's 44-hour arrival window does not.
    case.compare(500_000)
    assert 500_000 / (44 * 3600) > case.requests_per_second
    try:
        case.compare(case.capacity + 1)
    except ValueError:
        pass
    else:
        raise AssertionError("infeasible demand was accepted")
    print("Model checks passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    defaults = Assumptions()
    for name, value in vars(defaults).items():
        parser.add_argument("--" + name.replace("_", "-"), type=float, default=value)
    parser.add_argument("--requests", type=float, nargs="+", default=[10000, 100000, 500000])
    parser.add_argument("--check", action="store_true", help="run arithmetic checks, then print the requested comparison")
    args = vars(parser.parse_args())
    check = args.pop("check")
    requests = args.pop("requests")
    if check:
        check_model()
    try:
        case = Assumptions(**args)
        case.validate()
        print("ILLUSTRATIVE INPUTS — no measured hardware performance or market prices")
        for name, value in vars(case).items():
            print(f"{name}: {value:g}")
        print(f"Fixed monthly cost: ${case.fixed:.2f}")
        print(f"Incremental local cost/request: ${case.variable:.8f}")
        print(f"API cost/request: ${case.api:.6f}")
        print("Requests | Local USD | API USD | Assumed active hours")
        for count in requests:
            local, api = case.compare(count)
            print(f"{count:,.0f} | {local:.2f} | {api:.2f} | "
                  f"{count / (case.requests_per_second * 3600):.2f}")
        threshold = case.break_even
        if threshold is None:
            print("No volume break-even: API unit cost is no higher than local variable cost.")
        else:
            print(f"Arithmetic break-even: {threshold:,.2f} requests/month")
            if threshold > case.capacity:
                print("UNREACHABLE with assumed single-host capacity")
        print("Monthly capacity does not validate burst handling, uptime or latency.")
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
