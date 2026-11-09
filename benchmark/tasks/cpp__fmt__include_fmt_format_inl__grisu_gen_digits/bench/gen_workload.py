"""Seeded workload generator for grisu_gen_digits (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <item> TAB <item> ...   (reps = how many times the driver repeats the batch)
item = mode,value,precision
  mode 0: fixed number of digits (precision 0..17 digits after the point; value < 10^(17-precision)): the driver scales the value like format_float does
          and calls grisu_gen_digits(scaled, 1, exp, fixed_handler)
  mode 1: shortest representation: the driver builds the scaled upper boundary and the error like format_float does and
          calls grisu_gen_digits(upper, upper - lower, exp, grisu_shortest_handler)       (precision is ignored)
  value: decimal text of a positive finite double (strtod, exact)
The driver records the returned digits::result, the final exponent, the handler's size and the digits it wrote.
S: handcrafted values (ties, powers of ten, denormals); M/L: batches of random values.
"""
import random, struct, sys
from pathlib import Path

HAND = [1.0, 0.5, 1.5, 2.5, 0.125, 100.0, 1e22, 123.456, 0.001, 0.1, 0.3, 9.9996, 99.99, 0.9996, 5e-324, 2.2250738585072014e-308, 1.7976931348623157e308,
        1234567.0, 1e-5, 12345.6789, 4.35, 2.675, 1e15, 1e16, 3.141592653589793, 2.718281828459045, 0.7, 1e23, 8.41e21, 5e-5, 7.0, 0.99999999]


def rnd_value(rng):
    k = rng.random()
    if k < 0.4:
        bits = rng.getrandbits(63)
        e = (bits >> 52) & 0x7FF
        if e == 0x7FF:
            bits ^= 0x4000000000000000
        return abs(struct.unpack("<d", struct.pack("<Q", bits))[0]) or 1.0
    if k < 0.65:
        return rng.randrange(1, 10 ** rng.randrange(1, 12)) / 10.0 ** rng.randrange(0, 10)
    if k < 0.8:
        return float(rng.randrange(1, 10 ** rng.randrange(1, 20)))
    if k < 0.9:
        return rng.randrange(1, 2000) / 2.0 ** rng.randrange(0, 12)
    return rng.uniform(0.001, 10) * 10.0 ** rng.randrange(-8, 9)


def make_item(rng, v=None):
    if v is None:
        v = rnd_value(rng)
    mode = rng.choice([0, 0, 1, 1, 1])
    precision = rng.choice([0, 1, 2, 3, 4, 6, 6, 8, 10, 12, 15, 17]) if mode == 0 else 0
    if mode == 0 and v >= 10.0 ** (17 - precision):
        mode, precision = 1, 0   # keep fixed-digit items within 17 digits in total (the output buffer of the driver is small)
    return "%d,%s,%d" % (mode, repr(v), precision)


def lines(size, rng):
    reps, ncase, per = {"S": (1, 3, 10), "M": (10, 20, 300), "L": (10, 20, 3000)}[size]
    out = []
    if size == "S":
        items = [make_item(rng, v) for v in HAND for _ in range(3)]
        for i in range(0, len(items), 8):
            out.append("1\t" + "\t".join(items[i:i + 8]))
    for _ in range(ncase):
        out.append("%d\t" % reps + "\t".join(make_item(rng) for _ in range(per)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191202 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
