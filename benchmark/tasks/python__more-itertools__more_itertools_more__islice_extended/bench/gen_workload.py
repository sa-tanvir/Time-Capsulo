"""Seeded workload generator for islice_extended(). Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (1_500, 100), "M": (1_500, 2_000), "L": (300, 20_000)}   # (cases, max sequence length)

def bound(rng, length):
    r = rng.random()
    if r < 0.15:
        return None
    if r < 0.55:
        return rng.randint(0, length + 5)
    return -rng.randint(1, length + 5)

def cases(n_cases, max_len, rng):
    out = []
    for _ in range(n_cases):
        length = rng.randint(0, max_len)
        step = rng.choice([None, 1, 1, 2, 3, 7, -1, -1, -2, -5])
        nargs = rng.choice([1, 2, 3, 3, 3])
        if nargs == 1:
            args = [bound(rng, length)]
        elif nargs == 2:
            args = [bound(rng, length), bound(rng, length)]
        else:
            args = [bound(rng, length), bound(rng, length), step]
        out.append({"len": length, "args": args})
    return out

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, m, rng)))
