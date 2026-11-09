"""Seeded workload generator for isDurationValid(m) (validity of a normalized duration input object).
Usage: python3 gen_workload.py <out_dir>

Each case is an object as produced by normalizeObjectUnits: keys are mostly canonical unit names
(year ... millisecond), sometimes non-canonical ('isoWeek', 'days', 'foo'); values are integers, decimals,
numeric strings, null/undefined, NaN, +-Infinity, booleans or junk strings.
The object size is bounded by the unit set, so S/M/L scale the number of calls
(2,000 / 20,000 / 200,000 = 20,000 distinct objects used 10 times).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
UNITS = ["year", "quarter", "month", "week", "day", "hour", "minute", "second", "millisecond"]
SIZES = {"S": (2000, 1), "M": (20000, 1), "L": (20000, 10)}
NAN, UNDEF = {"$nan": 1}, {"$undef": 1}

FIXED = [{}, {"day": None}, {"day": 3.5, "hour": 1.1}, {"day": 3, "hour": 1.1}, {"millisecond": NAN},
         {"day": NAN}, {"isoWeek": 2}, {"days": 2}, {"year": 1, "month": 2, "day": 3, "hour": 4, "minute": 5,
         "second": 6, "millisecond": 7}, {"year": 1.5}, {"year": 1.5, "millisecond": 0}, {"year": 1.5, "millisecond": 2},
         {"hour": "1.5", "minute": 0}, {"hour": "1.5", "second": "3"}, {"month": "2"}, {"month": "abc"},
         {"day": {"$inf": 1}}, {"day": {"$inf": -1}, "hour": 1}, {"day": True, "hour": 2}, {"day": "", "hour": 2.5},
         {"second": "1e3", "millisecond": 5}, {"second": -2.5}, {"second": -2.5, "millisecond": -1}, {"week": UNDEF},
         {"week": 0.5, "day": 0, "hour": None}, {"quarter": " 4 ", "month": 1}, {"foo": 1}, {"day": 1, "foo": None}]


def value(rng):
    r = rng.random()
    if r < 0.45:
        return rng.randint(-1000, 1000)
    if r < 0.6:
        return round(rng.uniform(-100, 100), rng.randint(1, 3))
    if r < 0.7:
        return str(rng.choice([rng.randint(0, 99), round(rng.uniform(0, 9), 2)]))
    if r < 0.8:
        return rng.choice([None, UNDEF, 0, "0"])
    return rng.choice([NAN, {"$inf": 1}, {"$inf": -1}, True, False, "x", "", "1e2", "0x10", " 7"])


def case(rng):
    keys = rng.sample(UNITS, rng.randint(1, len(UNITS)))
    if rng.random() < 0.05:
        keys.append(rng.choice(["isoWeek", "days", "ms", "foo", "date"]))
    rng.shuffle(keys)
    o = {}
    for k in keys:
        o[k] = value(rng) if rng.random() < 0.5 else rng.randint(0, 60)
    return o


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, (size, (n, times)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cases = (list(FIXED) if size == "S" else []) + [case(rng) for _ in range(n)]
        (out / f"workload_{size}.json").write_text(json.dumps({"times": times, "cases": cases}, separators=(",", ":")))
