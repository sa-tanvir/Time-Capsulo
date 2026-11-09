"""Seeded workload generator for merge_setting. Usage: python3 gen_workload.py <out_dir>"""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (200, 10), "M": (200, 100), "L": (200, 1000)}   # (cases, max keys per mapping)


def key(rng, pool):
    k = rng.choice(pool)
    return k.upper() if rng.random() < 0.2 else k


def mapping(rng, pool, n):
    return [[key(rng, pool), None if rng.random() < 0.15 else "v" + str(rng.randint(0, 999))]
            for _ in range(rng.randint(0, n))]


def side(rng, pool, n):
    r = rng.random()
    if r < 0.08:
        return {"t": "none"}
    if r < 0.14:
        return {"t": "scalar", "v": rng.choice([True, False, "/path/ca.pem", 5])}
    return {"t": rng.choice(["odict", "dict"]), "v": mapping(rng, pool, n)}


def case(rng, n):
    pool = ["X-" + "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(2, 8))) for _ in range(max(2, n))]
    return {"req": side(rng, pool, n), "ses": side(rng, pool, n),
            "cls": rng.choice(["default", "odict", "cid", "cid", "dict"])}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, c)) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, c) for _ in range(n)]))
