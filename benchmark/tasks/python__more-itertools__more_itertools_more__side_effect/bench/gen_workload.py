"""Seeded workload generator for side_effect(). Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (60, 300), "M": (60, 10_000), "L": (60, 40_000)}   # (cases, max length)

def case(rng, max_len):
    return {"data": [rng.randint(-1000, 1000) for _ in range(rng.randint(0, max_len))],
            "chunk": rng.choice([None, None, 1, 2, 3, 16, 100]),
            "before": rng.random() < 0.5, "after": rng.random() < 0.5,
            "fail_at": rng.choice([None, None, None, rng.randint(0, max_len)])}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, m) for _ in range(n)]))
