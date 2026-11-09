"""Seeded workload generator for _ymd.resolve_ymd. Usage: python3 gen_workload.py <out_dir>
Each case: [yearfirst, dayfirst, [[value, label], ...]] where label is null/"M"/"D"/"Y"."""
import json, random, sys
from pathlib import Path

SIZES = {"S": 2_000, "M": 20_000, "L": 200_000}   # number of _ymd objects


def entry(rng, role):
    if role == "y":
        if rng.random() < 0.5:
            return [rng.randint(1900, 2099), "Y" if rng.random() < 0.3 else None]
        return [rng.randint(0, 99), None]
    if role == "m":
        return [rng.randint(1, 12), "M" if rng.random() < 0.45 else None]
    return [rng.randint(1, 31), "D" if rng.random() < 0.05 else None]


def make_case(rng):
    r = rng.random()
    if r < 0.005:
        vals = [[rng.randint(1, 31), None] for _ in range(4)]
    elif r < 0.01:
        vals = []
    else:
        n = rng.choice([1, 2, 2, 3, 3, 3, 3, 3])
        roles = rng.sample(["y", "m", "d"], n)
        vals = [entry(rng, x) for x in roles]
        if rng.random() < 0.1:   # arbitrary small numbers (ambiguous / out of range)
            vals = [[rng.randint(1, 60), None] for _ in range(n)]
    # at most one entry per label
    seen = set()
    for v in vals:
        if v[1] is not None:
            if v[1] in seen:
                v[1] = None
            seen.add(v[1])
        if v[0] > 100 and v[1] not in (None, "Y"):
            v[1] = None
    if any(v[0] > 100 for v in vals) and "Y" in seen:
        for v in vals:
            if v[1] == "Y" and v[0] <= 100:
                v[1] = None
    if sum(1 for v in vals if v[0] > 100 or v[1] == "Y") > 1:
        vals = [[min(v[0], 99), None if v[1] == "Y" else v[1]] for v in vals]
    return [rng.random() < 0.3, rng.random() < 0.3, vals]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, n) in enumerate(SIZES.items()):
        rng = random.Random(20191103 + i)
        cases = [make_case(rng) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases, separators=(",", ":")))
