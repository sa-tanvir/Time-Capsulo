"""Seeded workload generator for snprintf_float (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <item> TAB <item> ...   (reps = how many times the driver repeats the batch)
item = value,precision,format,upper,trailing_zeros,use_grisu,binary32,long_double,prefix
  value: decimal text of a non-negative finite number (parsed with strtod / strtold, so every double is exact)
  precision: argument `precision`; format: 0 general, 1 exp, 2 fixed, 3 hex; upper, trailing_zeros, use_grisu, binary32, long_double: 0/1
  prefix: 1 = the output buffer already holds the character '-' before the call (only used with the hex format)
Constraints: value >= 0 and finite; precision -1 or >= 0 (for general/exp the effective precision is precision - 1 digits after the first); the
buffer is empty on entry except for the hex format, where it may already hold '-' (prefix=1).
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
        elif False and not (900 < e < 1150):
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
    ld = rng.random() < 0.25
    fmt = rng.choice([0, 1, 2, 3])
    precision = rng.choice([-1, 0, 1, 2, 3, 5, 6, 10, 15, 17, 20, 30]) if fmt != 3 else rng.choice([-1, -1, 0, 1, 4, 13])
    prefix = 1 if fmt == 3 and rng.random() < 0.5 else 0
    return "%s,%d,%d,%d,%d,%d,0,%d,%d" % (repr(v), precision, fmt, rng.choice([0, 1]) if fmt == 3 else 0, rng.choice([0, 1]), rng.choice([0, 1]), 1 if ld else 0, prefix)


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
