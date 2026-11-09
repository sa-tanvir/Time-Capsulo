"""Seeded workload generator for pickBy(fn, moments) (backs moment.min / moment.max).
Usage: python3 gen_workload.py <out_dir>

Each case is [fn, wrapped, values]: fn is 'isBefore' (min) or 'isAfter' (max); wrapped=true passes the
moments as a single array argument ([[m0, m1, ...]]); values are epoch milliseconds (UTC) or null for an
invalid moment. Lists are never empty. S/M/L grow the list length (~10 / ~100 / ~1000 moments).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
SIZES = {"S": (600, 10), "M": (300, 100), "L": (150, 1000)}
BASE = 1548028800000  # 2019-01-21T00:00:00Z
MONTH = 30 * 86400000

FIXED = []
for fn in ("isBefore", "isAfter"):
    for wrapped in (False, True):
        FIXED += [[fn, wrapped, v] for v in (
            [BASE, BASE + MONTH, BASE - MONTH], [BASE + MONTH, BASE, BASE - MONTH], [BASE + MONTH, BASE - MONTH, BASE],
            [BASE - MONTH, BASE + MONTH, BASE], [BASE, BASE - MONTH], [BASE - MONTH, BASE], [BASE],
            [BASE, None], [None, BASE], [None], [BASE, BASE, BASE], [BASE, None, BASE - 5, None, BASE + 5],
            [0, -1, 1], [8.64e15, -8.64e15])]


def case(rng, n):
    n = max(1, rng.randint(n // 2, n * 3 // 2))
    if rng.random() < 0.3:
        vals = [BASE + rng.randint(-20, 20) * 1000 for _ in range(n)]  # many ties
    else:
        vals = [rng.randint(-10 ** 13, 10 ** 13) for _ in range(n)]
    if rng.random() < 0.2:
        vals.sort(reverse=rng.random() < 0.5)
    if rng.random() < 0.3:
        for _ in range(rng.randint(1, 3)):
            vals[rng.randrange(n)] = None
    return [rng.choice(["isBefore", "isAfter"]), rng.random() < 0.5, vals]


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, (size, (count, n)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cases = (list(FIXED) if size == "S" else []) + [case(rng, n) for _ in range(count)]
        (out / f"workload_{size}.json").write_text(json.dumps(cases, separators=(",", ":")))
