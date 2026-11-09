"""Seeded workload generator for humanize.Commaf. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, decimal-exponent range): output length grows ~10x per size
SIZES = {"S": (6_000, 0, 6), "M": (6_000, 10, 40), "L": (6_000, 100, 300)}
EDGE = [0.0, -0.0, 10.11, 100.0, 1000.0, 10000.0, 100000.0, 834142.32, 10000000.0, 10100000.0, 10010000.0,
        10001000.0, 123456789.0, 999.5, 0.5, -0.25, 123456.5, 1e21, 1e-7, 1.7976931348623157e308, 5e-324,
        -123456789.0, -10100000.0, -1000.0, -100.11, -10.0, 1.23]

def value(rng, lo, hi):
    e = rng.randint(lo, hi)
    if rng.random() < 0.3:
        e = -e  # small magnitudes give long fractional parts
    m = rng.choice([rng.random(), float(rng.randint(1, 999)), round(rng.uniform(1, 1000), rng.randint(0, 6))])
    v = float(f"{m}e{e}")
    if v == 0.0 or v != v or v in (float("inf"), float("-inf")):
        v = 1.5
    return -v if rng.random() < 0.4 else v

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20180713 + i)
        vals = list(EDGE) if size == "S" else []
        while len(vals) < n:
            vals.append(value(rng, lo, hi))
        # repr() round-trips exactly, so Go's json parser recovers the same float64
        (out_dir / f"workload_{size}.json").write_text("{\"values\": [" + ", ".join(repr(v) for v in vals) + "]}")
