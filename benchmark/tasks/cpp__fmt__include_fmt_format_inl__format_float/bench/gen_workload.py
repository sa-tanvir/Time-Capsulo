"""Seeded workload generator for format_float (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <item> TAB <item> ...   (reps = how many times the driver repeats the batch)
item = value,precision,format,upper,trailing_zeros,use_grisu,binary32,long_double,prefix
  value: decimal text of a non-negative finite number (parsed with strtod / strtold, so every double is exact)
  precision: argument `precision`; format: 0 general, 1 exp, 2 fixed; upper, trailing_zeros, use_grisu, binary32, long_double: 0/1
  prefix: 1 = the output buffer already holds the character '-' before the call (only used with the hex format)
Constraints (they follow the callers): value > 0 or == 0, never negative/NaN/inf; format is general/exp/fixed (no hex); fixed never has
precision -1; general/exp use precision -1 or >= 1; binary32 is never set; fixed with precision 0 has no trailing_zeros; fixed items whose integer digits plus precision exceed 17 use use_grisu = 0; long double
items have use_grisu = 0; the buffer is empty on entry.
S: handcrafted values plus random ones; M/L: batches of random values.
"""
import random, struct, sys
from pathlib import Path

HAND = [0.0, 1.0, 0.5, 1.5, 2.5, 0.125, 0.375, 100.0, 1e22, 1e23, 123.456, 0.001, 0.1, 0.2, 0.3, 9.9996, 99.99, 0.9996, 5e-324, 2.2250738585072014e-308,
        1.7976931348623157e308, 1234567.0, 1e-5, 12345.6789, 0.000123456, 4.35, 2.675, 1e15, 1e16, 123456789012345678.0, 3.141592653589793, 2.718281828459045]


def rnd_value(rng):
    k = rng.random()
    if k < 0.35:
        bits = rng.getrandbits(64) & 0x7FFFFFFFFFFFFFFF
        e = (bits >> 52) & 0x7FF
        if e == 0x7FF:
            bits ^= 0x4000000000000000
        elif True and not (900 < e < 1150):
            bits = (bits & 0x800FFFFFFFFFFFFF) | (rng.randrange(900, 1150) << 52)
        v = struct.unpack("<d", struct.pack("<Q", bits))[0]
    elif k < 0.6:
        v = rng.randrange(0, 10 ** rng.randrange(1, 12)) / 10.0 ** rng.randrange(0, 10)
    elif k < 0.75:
        v = float(rng.randrange(0, 10 ** rng.randrange(1, 20)))
    elif k < 0.85:
        v = rng.randrange(0, 2000) / 2.0 ** rng.randrange(0, 12)
    else:
        v = rng.uniform(0, 10) * 10.0 ** rng.randrange(-8, 9)
    return abs(v)


def make_item(rng, v=None):
    if v is None:
        v = rnd_value(rng)
    ld = rng.random() < 0.2
    fmt = rng.choice([0, 1, 2, 2, 2])
    grisu = 0 if ld else (1 if rng.random() < 0.85 else 0)
    if fmt == 2:
        precision = rng.choice([0, 1, 2, 3, 4, 6, 6, 8, 10, 15, 17, 18, 20])
    else:
        precision = rng.choice([1, 2, 3, 5, 6, 7, 9, 12, 15, 17, 18, 20, -1, -1, -1])
    if precision == -1 and fmt == 2:
        precision = 6
    # the fast digit generator is only exact up to 17 digits in total: keep fixed items with more integer digits on the snprintf path
    if fmt == 2 and 0 <= precision <= 17 and v >= 10.0 ** (17 - precision):
        grisu = 0
    tz = rng.choice([0, 1])
    if fmt == 2 and precision == 0:
        tz = 0
    return "%s,%d,%d,0,%d,%d,0,%d,0" % (repr(v), precision, fmt, tz, grisu, 1 if ld else 0)


def lines(size, rng):
    reps, ncase, per = {"S": (1, 4, 10), "M": (10, 20, 300), "L": (10, 20, 3000)}[size]
    out = []
    if size == "S":
        for i, v in enumerate(HAND):
            out.append(None)
        hand_items = [make_item(rng, v) for v in HAND for _ in range(2)]
        for i in range(0, len(hand_items), 8):
            out.append("1\t" + "\t".join(hand_items[i:i + 8]))
        out = [o for o in out if o]
    for _ in range(ncase):
        out.append("%d\t" % reps + "\t".join(make_item(rng) for _ in range(per)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191202 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
