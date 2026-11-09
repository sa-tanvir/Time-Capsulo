"""Seeded workload generator for windowed(). Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (20, 200), "M": (60, 2_000), "L": (60, 20_000)}   # (cases, max sequence length)

def cases(n_cases, max_len, rng):
    out = []
    for _ in range(n_cases):
        length = rng.randint(0, max_len)
        out.append({
            "seq": [rng.randint(-1000, 1000) for _ in range(length)],
            "n": rng.choice([0, 1, 2, 3, 5, 8, 16, 64]),
            "step": rng.choice([1, 1, 1, 2, 3, 7]),
            "fillvalue": rng.choice([None, 0, -1]),
        })
    return out

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, m, rng)))
