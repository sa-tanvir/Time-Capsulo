"""Seeded workload generator for humanize.BigComma. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, min digits, max digits): per-case digit count grows ~10x per size
SIZES = {"S": (6_000, 1, 20), "M": (2_000, 20, 200), "L": (600, 200, 2_000)}
EDGE = [0, 10, 100, 999, 1000, 10000, 100000, 10000000, 10100000, 10010000, 10001000, 123456789,
        9223372000000000000, -9223372000000000000, -123456789, -1000, -100, -10, -1, 2**64, -2**63,
        10**12, 84889279597249724975972597249849757294578485, -84889279597249724975972597249849757294578485]

def value(rng, lo, hi):
    d = rng.randint(lo, hi)
    s = str(rng.randint(1, 9)) + "".join(rng.choice("0123456789") for _ in range(d - 1))
    if rng.random() < 0.15:  # runs of zero groups
        k = rng.randint(0, len(s) - 1)
        s = s[:k] + "0" * (len(s) - k)
        s = s if s[0] != "0" else "1" + s[1:]
    return ("-" if rng.random() < 0.4 else "") + s

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20180713 + i)
        vals = [str(v) for v in EDGE] if size == "S" else []
        while len(vals) < n:
            vals.append(value(rng, lo, hi))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"values": vals}))
