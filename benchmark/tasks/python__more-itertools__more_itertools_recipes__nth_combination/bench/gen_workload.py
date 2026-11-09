"""Seeded workload generator for nth_combination(). Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from math import factorial
from pathlib import Path

SIZES = {"S": (1_500, 60), "M": (1_200, 300), "L": (2_500, 1_200)}   # (cases, max pool size)

def comb(n, r):
    return factorial(n) // (factorial(r) * factorial(n - r))

def case(rng, max_n):
    n = rng.randint(0, max_n)
    r = rng.randint(0, n)
    c = comb(n, r)
    roll = rng.random()
    if roll < 0.04:                       # invalid r
        return {"n": n, "r": rng.choice([-1, n + 1]), "index": 0}
    if roll < 0.08:                       # index out of range (as decimal string: may exceed 2**53)
        return {"n": n, "r": r, "index": str(rng.choice([c, -c - 1]))}
    idx = rng.randrange(c)
    if rng.random() < 0.3:
        idx -= c
    return {"n": n, "r": r, "index": str(idx)}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (k, m)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, m) for _ in range(k)]))
