"""Seeded workload generator for RequestEncodingMixin._encode_params. Usage: python3 gen_workload.py <out_dir>"""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (100, 10), "M": (100, 100), "L": (100, 1000)}   # (cases, max pairs per case)
CHARS = string.ascii_letters + string.digits + " _.-~&=+/?#%:;@!äöüøß€日本"


def text(rng, lo=0, hi=12):
    return "".join(rng.choice(CHARS) for _ in range(rng.randint(lo, hi)))


def scalar(rng):
    r = rng.random()
    if r < 0.55:
        return {"s": text(rng)}
    if r < 0.70:
        return {"b": text(rng)}
    if r < 0.82:
        return {"i": rng.randint(-10**6, 10**6)}
    if r < 0.88:
        return {"f": round(rng.uniform(-1000, 1000), 3)}
    return None


def value(rng):
    if rng.random() < 0.25:
        return {"list": [scalar(rng) for _ in range(rng.randint(0, 5))]}
    return scalar(rng)


def case(rng, maxp):
    r = rng.random()
    if r < 0.05:
        return {"kind": "raw_str", "v": text(rng, 0, 40)}
    if r < 0.08:
        return {"kind": "raw_bytes", "v": text(rng, 0, 40)}
    if r < 0.10:
        return {"kind": rng.choice(["none", "int"])}
    n = rng.randint(0, maxp)
    pairs = []
    for _ in range(n):
        key = {"b": text(rng, 1, 8)} if rng.random() < 0.15 else {"s": text(rng, 1, 8)}
        pairs.append([key, value(rng)])
    return {"kind": rng.choice(["dict", "pairs", "tuples"]), "v": pairs}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, maxp)) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, maxp) for _ in range(n)]))
