"""Seeded workload generator for iter_except(). Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (300, 200), "M": (300, 3_000), "L": (300, 30_000)}   # (cases, max items)

def case(rng, max_items):
    source = rng.choice(["pop", "popleft", "next"])
    # an escaping StopIteration has implementation-dependent semantics (PEP 479), so "wrong" only for pops
    excs = ["exact", "base", "tuple"] + (["wrong"] if source != "next" else [])
    return {"data": [rng.randint(-10**6, 10**6) for _ in range(rng.randint(0, max_items))],
            "source": source,
            "exc": rng.choice(excs),
            "first": rng.choice([None, None, rng.randint(0, 99)])}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, m) for _ in range(n)]))
