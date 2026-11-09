"""Seeded workload generator for humanize.oomm. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, min digits, max digits) of n: per-case size grows ~10x per size
SIZES = {"S": (6_000, 1, 30), "M": (1_500, 30, 300), "L": (200, 300, 3_000)}
EDGE = [[5, 10, -1], [999, 1000, 8], [1500, 1000, 8], [12345, 10, -1], [12345, 10, 0], [12345, 10, 2],
        [123456789, 1000, 1], [5242880, 1024, 1], [5242880, 1024, 8], [1024, 1000, 8], [0, 1000, 8],
        [1000, 1000, 8], [15347691069326346944512, 1000, 8], [15347691069326346944512, 1024, 8],
        [16093220510709943573688614912, 1000, 8], [16093220510709943573688614912, 1024, 8]]
LIMIT = 2 ** 62

def full_mag(n, b):
    m = 0
    while n >= b:
        n //= b
        m += 1
    return m

def case(rng, lo, hi):
    d = rng.randint(lo, hi)
    n = int(str(rng.randint(1, 9)) + "".join(rng.choice("0123456789") for _ in range(d - 1)))
    b = rng.choice([10, 1000, 1024, 2, 16, rng.randint(2, 100), rng.randint(2, 10 ** 6)])
    k = rng.random()
    if k < 0.4:
        cap = rng.choice([-1, 0])
    else:
        m = full_mag(n, b)
        # smallest cap that keeps the final quotient within int64
        lo_cap = m
        while lo_cap > 1 and n // b ** (lo_cap - 1) < LIMIT:
            lo_cap -= 1
        cap = rng.randint(max(1, lo_cap), max(1, m + 3))
        if n // b ** min(cap, m) >= LIMIT:
            cap = -1
    return [str(n), b, cap]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (cnt, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20180713 + i)
        cases = [[str(a), b, c] for a, b, c in EDGE] if size == "S" else []
        while len(cases) < cnt:
            cases.append(case(rng, lo, hi))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
