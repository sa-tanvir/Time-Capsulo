"""Seeded workload generator for bucket._get_values (via bucket[...]). Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (40, 400), "M": (50, 6_000), "L": (50, 60_000)}   # (cases, max source length)

def case(rng, max_len):
    k = rng.choice([2, 3, 5, 10, 50])
    n = rng.randint(0, max_len)
    data = [rng.randint(0, 10**6) for _ in range(n)]
    valid = rng.random() < 0.4
    # access plan: list of [bucket, how_many] ; how_many -1 means "drain"; "in" probes use how_many -2
    plan = []
    for _ in range(rng.randint(1, 3 * k)):
        b = rng.randrange(k + 2)          # k, k+1 never occur
        r = rng.random()
        plan.append([b, -1 if r < 0.3 else (-2 if r < 0.4 else rng.randint(1, max(1, n // k)))])
    return {"data": data, "k": k, "valid_odd_only": valid, "plan": plan}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (c, m)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, m) for _ in range(c)]))
