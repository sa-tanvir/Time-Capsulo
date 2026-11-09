"""Seeded workload generator for isoparser._parse_isotime. Usage: python3 gen_workload.py <out_dir>
Each case is an ASCII time string (the driver encodes it to bytes, as isoparse does)."""
import json, random, sys
from pathlib import Path

SIZES = {"S": 2_000, "M": 20_000, "L": 200_000}   # number of time strings


def tzpart(rng):
    r = rng.random()
    if r < 0.45:
        return ""
    if r < 0.6:
        return rng.choice("Zz")
    sign = rng.choice("+-")
    hh, mm = rng.randint(0, 23), rng.choice([0, 0, 15, 30, 45, rng.randint(0, 59)])
    if rng.random() < 0.02:   # invalid offsets
        hh, mm = rng.choice([(rng.randint(24, 99), mm), (hh, rng.randint(60, 99))])
    form = rng.randint(0, 2)
    if form == 0:
        return "%s%02d" % (sign, hh)
    if form == 1:
        return "%s%02d%02d" % (sign, hh, mm)
    return "%s%02d:%02d" % (sign, hh, mm)


def valid(rng):
    h = 24 if rng.random() < 0.03 else rng.randint(0, 23)
    m, s = rng.randint(0, 59), rng.randint(0, 59)
    if h == 24 and rng.random() < 0.7:
        m = s = 0
    sep = ":" if rng.random() < 0.6 else ""
    n = rng.choice([1, 2, 3, 3, 3])
    out = "%02d" % h
    if n >= 2:
        out += sep + "%02d" % m
    if n >= 3:
        out += sep + "%02d" % s
        if rng.random() < 0.6:
            nd = rng.choice([1, 2, 3, 3, 6, 6, 6, 9, 12])
            frac = "".join(rng.choice("0123456789") for _ in range(nd))
            if h == 24 and m == 0 and s == 0 and rng.random() < 0.7:
                frac = "0" * nd
            out += rng.choice(".,") + frac
    return out + tzpart(rng)


def invalid(rng):
    base = valid(rng)
    r = rng.randint(0, 5)
    if r == 0:
        return rng.choice(["", "1", "9"])
    if r == 1:
        return "%02d:%02d:%02d." % (rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59))
    if r == 2:
        return "%02d:%02d:%02d:%02d" % tuple(rng.randint(0, 59) for _ in range(4))
    if r == 3:
        return "%02d:%02d:%02d.%d:00" % (rng.randint(0, 23), rng.randint(0, 59),
                                         rng.randint(0, 59), rng.randint(1, 99999999))
    if r == 4:
        return "%02d%02d%02d%s" % (rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59),
                                   rng.choice(["+", "-", "+1234567", "+123"]))
    return "24:%02d:%02d" % (rng.randint(1, 59), rng.randint(0, 59))


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, n) in enumerate(SIZES.items()):
        rng = random.Random(20191103 + i)
        cases = [invalid(rng) if rng.random() < 0.08 else valid(rng) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases, separators=(",", ":")))
