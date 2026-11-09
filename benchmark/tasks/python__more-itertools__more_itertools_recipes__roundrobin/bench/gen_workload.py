"""Seeded workload generator for roundrobin(). Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (600, 8, 500), "M": (200, 40, 8_000), "L": (80, 200, 20_000)}   # (cases, max #iterables, max total items)

def case(rng, max_k, max_total):
    k = rng.randint(0, max_k)
    total = rng.randint(0, max_total)
    if k == 0:
        return []
    shape = rng.choice(["even", "random", "skewed"])
    if shape == "even":
        lens = [total // k] * k
    elif shape == "random":
        lens = [rng.randint(0, 2 * total // k) for _ in range(k)]
    else:
        lens = [int(total * rng.random() ** 4) // k for _ in range(k)]
    return lens

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k, t)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, k, t) for _ in range(n)]))
