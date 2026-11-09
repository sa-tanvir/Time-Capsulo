"""Seeded workload generator for float_writer::prettify (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <item> TAB <item> ...
item = digits,exp,precision,format,sign,upper,trailing_zeros,point
  digits: decimal digit string (the shortest/rounded digits of a number; first digit non-zero except the single digit "0")
  exp: decimal exponent: value = digits * 10^exp
  precision: float_specs.precision (-1 = none); format: 0 general, 1 exp, 2 fixed; sign: 0 none, 1 '-', 2 '+', 3 ' '
  upper, trailing_zeros: 0/1; point: the decimal point character
The driver builds a float_writer<char>, records size() and the characters written by operator() (prettify runs twice: once in
the constructor to compute the size, once to write).
S: 40 handcrafted + random items per size; M/L: batches of random items.
"""
import random, sys
from pathlib import Path

HAND = [("1", 0, -1, 0, 0, 0, 0), ("12345", -4, -1, 0, 0, 0, 0), ("12345", 3, -1, 0, 0, 0, 0), ("1234", -2, 6, 2, 0, 0, 1), ("1", -7, 12, 0, 0, 1, 0),
        ("1", 20, -1, 0, 0, 0, 0), ("12", -20, 3, 1, 1, 0, 1), ("5", 2, 8, 2, 2, 0, 1), ("1500", -3, 6, 2, 3, 0, 0), ("0", 0, 6, 2, 0, 0, 1), ("0", 0, -1, 0, 0, 0, 0),
        ("123", 1, 2, 1, 0, 1, 1), ("1", 0, 5, 1, 0, 0, 1), ("1", 0, 5, 1, 0, 0, 0), ("100", -2, -1, 2, 0, 0, 0), ("1000", -3, 4, 2, 0, 0, 1),
        ("123456789", -3, 3, 2, 0, 0, 1), ("123456789", -9, -1, 0, 0, 0, 0), ("9", 300, -1, 1, 0, 0, 0), ("17", -330, -1, 0, 2, 0, 0)]


def rdigits(rng):
    n = rng.choice([1, 1, 2, 3, 5, 8, 12, 16, 17, 17, 20])
    d = rng.choice("123456789") + "".join(rng.choice("0000123456789") for _ in range(n - 1))
    if rng.random() < 0.3:
        d = d.rstrip("0") or "1"
        d += "0" * rng.choice([0, 1, 2, 4])
    return d


def item(rng):
    d = rdigits(rng)
    fmt = rng.choice([0, 0, 1, 2, 2])
    if fmt == 1 or (fmt == 0 and rng.random() < 0.3):
        exp = rng.randrange(-340, 300)
    else:
        exp = rng.randrange(-25, 25)
    if fmt == 2:
        exp = max(min(exp, 40), -40)
    precision = rng.choice([-1, -1, 0, 1, 3, 6, 6, 10, 17, 20, 30])
    return "%s,%d,%d,%d,%d,%d,%d,%s" % (d, exp, precision, fmt, rng.choice([0, 0, 1, 2, 3]), rng.choice([0, 0, 1]), rng.choice([0, 1]), rng.choice("....;"))


def lines(size, rng):
    reps, ncase, per = {"S": (1, 6, 12), "M": (10, 20, 400), "L": (10, 20, 4000)}[size]
    out = []
    if size == "S":
        hand = ["%s,%d,%d,%d,%d,%d,%d,." % h for h in HAND]
        for i in range(0, len(hand), 10):
            out.append("1\t" + "\t".join(hand[i:i + 10]))
    for _ in range(ncase):
        out.append("%d\t" % reps + "\t".join(item(rng) for _ in range(per)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191202 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
