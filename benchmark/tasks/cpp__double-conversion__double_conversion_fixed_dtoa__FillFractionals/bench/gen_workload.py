"""Seeded workload generator for FillFractionals (double-conversion). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines: <reps> <seed> <n> <maxcount>. The driver builds n calls: exponent in [-128, 0], fractionals below
2^-exponent (and below 2^53), fractional_count in [0, maxcount], plus a prefix of digits already in the buffer (mostly 9s) and an initial
decimal_point.
"""
import random, sys
from pathlib import Path


SIZES = {"S": (6, 100, 2), "M": (20, 1000, 4), "L": (100, 1000, 30)}


def lines(size, rng):
    maxc, n, nl = SIZES[size]
    return ["1\t%d\t%d\t%d\t%d" % (rng.randrange(1, 2**62), n, maxc, 0) if False else "1\t%d\t%d\t%d" % (rng.randrange(1, 2**62), n, maxc) for _ in range(nl)]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190920 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
