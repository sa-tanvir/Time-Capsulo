"""Seeded workload generator for Request.__init__. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (300, 10), "M": (300, 100), "L": (300, 1000)}   # (cases, max hooks per case)
ARGS = ["method", "url", "headers", "files", "data", "params", "auth", "cookies", "json"]


def case(rng, n):
    present = {a: rng.random() < 0.5 for a in ARGS}
    r = rng.random()
    if r < 0.15:
        hooks = None
    elif r < 0.20:
        hooks = {"kind": "bad"}
    elif r < 0.30:
        hooks = {"kind": "single", "fn": rng.randint(0, 7)}
    else:
        items = [rng.randint(0, 7) if rng.random() < 0.85 else -1 for _ in range(rng.randint(0, n))]
        hooks = {"kind": rng.choice(["list", "tuple"]), "items": items}
    return {"present": present, "hooks": hooks, "falsy": rng.random() < 0.2}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, c)) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, c) for _ in range(n)]))
