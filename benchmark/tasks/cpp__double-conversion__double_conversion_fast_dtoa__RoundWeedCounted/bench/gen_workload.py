"""Seeded workload generator for RoundWeedCounted (double-conversion). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines: <reps> <seed> <n> <bits>. The driver builds n calls (rest < ten_kappa < 2^bits, unit from tiny to larger than ten_kappa)
with a digit buffer of 1..17 digits that often contains 9s (carry propagation) and an initial kappa.
"""
import random, sys
from pathlib import Path


SIZES = {"S": (16, 200, 3), "M": (36, 2000, 6), "L": (60, 50000, 40)}


def lines(size, rng):
    bits, n, nl = SIZES[size]
    return ["1\t%d\t%d\t%d" % (rng.randrange(1, 2**62), n, bits) for _ in range(nl)]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190920 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
