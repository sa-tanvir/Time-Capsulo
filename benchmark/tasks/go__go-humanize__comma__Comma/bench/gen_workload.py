"""Seeded workload generator for humanize.Comma. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (distinct values, inner repetitions per pass)
SIZES = {"S": (20_000, 1), "M": (50_000, 2), "L": (50_000, 20)}
EDGE = [0, 1, -1, 9, 10, 99, 100, 999, 1000, -999, -1000, 1001, 10001000, 10010000, 10100000,
        -10001000, 123456789, -123456789, 2**63 - 1, -2**63, -2**63 + 1, 9223372000000000000,
        -9223372000000000000]

def values(n, rng):
    out = list(EDGE)
    while len(out) < n:
        digits = rng.randint(1, 19)
        v = rng.randint(10 ** (digits - 1) if digits > 1 else 0, min(10 ** digits - 1, 2**63 - 1))
        out.append(-v if rng.random() < 0.4 else v)
    return out

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, inner)) in enumerate(SIZES.items()):
        rng = random.Random(20180713 + i)
        # int64 values are stored as strings so no JSON parser loses precision
        doc = {"inner": inner, "values": [str(v) for v in values(n, rng)]}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(doc))
