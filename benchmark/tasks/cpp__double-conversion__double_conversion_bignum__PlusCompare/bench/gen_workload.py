"""Seeded workload generator for Bignum::PlusCompare (double-conversion). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines parsed by driver.cpp:
  L <reps> <a> <b> <c>                          operands as hex digits, optionally "@k" = shifted left by k*28 bits
  G <reps> <seed> <n> <maxdigits> <maxshift>    n triples (a, b, c) built by the driver from splitmix64: random hex operands of up to
      <maxdigits> hex digits, optional shifts of up to <maxshift> bigits, and c = a+b, a+b+-small, unrelated values, a, 2b, 2(a+b) ...
"""
import random, sys
from pathlib import Path


LITERALS = [("0", "0", "0"), ("0", "0", "1"), ("1", "0", "0"), ("1", "1", "2"), ("1", "1", "1"), ("1", "1", "3"), ("fffffff", "1", "10000000"),
            ("fffffff", "1", "fffffff"), ("fffffff", "1", "10000001"), ("10000000", "10000000", "20000000"), ("ffffffff", "ffffffff", "1fffffffe"),
            ("1@3", "1@3", "2@3"), ("1@3", "1", "1@3"), ("1@3", "1", "1000000000000000000000001"), ("1@3", "1", "1000000000000000000000000"),
            ("1@3", "1", "1000000000000000000000002"), ("1@5", "ff@1", "1@5"), ("ff@1", "1@5", "100000000000000000000ff0000000"),
            ("123456789abcdef", "fedcba987654321", "222222222222220"), ("123456789abcdef", "fedcba987654321", "222222222222222"),
            ("123456789abcdef", "fedcba987654321", "222222222222221"), ("1@10", "1@10", "1@10"), ("1", "1@10", "1@10"), ("1@10", "1", "1@10"),
            ("abc", "0", "abc"), ("0", "abc", "abd"), ("0", "abc", "abb"), ("1000000000000000000000000000", "1", "1000000000000000000000000001")]
SIZES = {"S": (1, 60, 12, 3, 3), "M": (1, 300, 90, 8, 8), "L": (1, 300, 700, 5, 6)}   # reps, n per line, maxdigits, maxshift, lines


def lines(size, rng):
    reps, n, maxd, maxs, nl = SIZES[size]
    out = []
    if size == "S":
        for a, b, c in LITERALS:
            out.append("L\t1\t%s\t%s\t%s" % (a, b, c))
    for _ in range(nl):
        out.append("G\t%d\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), n, maxd, maxs))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190920 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
