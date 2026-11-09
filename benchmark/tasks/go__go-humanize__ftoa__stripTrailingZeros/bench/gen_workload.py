"""Seeded workload generator for humanize.stripTrailingZeros. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, max fractional length): same case count, per-case length grows ~10x per size
SIZES = {"S": (6_000, 12), "M": (6_000, 120), "L": (6_000, 1_200)}
EDGE = ["0.000000", "-0.000000", "2.000000", "2.200000", "2.020000", "200.000000", "200.020000",
        "2.234500", "7.", "1.23", "100.0", "10.010", "3.14159", "-12.500", "0.", "1000000.000001"]

def case(rng, maxfrac):
    ip = str(rng.randint(0, 10 ** rng.randint(1, 12)))
    if rng.random() < 0.3:
        ip = ip + "0" * rng.randint(1, 4)
    flen = rng.randint(0, maxfrac)
    zeros = rng.randint(0, flen) if rng.random() < 0.8 else 0
    body = "".join(rng.choice("0123456789") for _ in range(flen - zeros))
    if body and rng.random() < 0.9:
        body = body[:-1] + rng.choice("123456789")
    sign = "-" if rng.random() < 0.3 else ""
    return sign + ip + "." + body + "0" * zeros

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, maxfrac)) in enumerate(SIZES.items()):
        rng = random.Random(20180713 + i)
        vals = list(EDGE) if size == "S" else []
        while len(vals) < n:
            vals.append(case(rng, maxfrac))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"values": vals}))
