"""Seeded workload generator for DoubleToStringConverter::ToPrecision (double-conversion). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines: <reps> <seed> <n> <maxd>. The driver builds n calls (see driver.cpp): one of 12 converter configurations (flags,
infinity/NaN symbols or none, exponent character, padding limits), a value (random bit patterns, short decimals, integers, +-0, inf, nan, extremes)
and a digit count in the valid range up to <maxd> (about 1 call in 25 uses an out-of-range count, which must make the function return false).
"""
import random, sys
from pathlib import Path


SIZES = {"S": (6, 100, 2), "M": (20, 1000, 3), "L": (120, 2000, 6)}


def lines(size, rng):
    maxd, n, nl = SIZES[size]
    return ["1\t%d\t%d\t%d" % (rng.randrange(1, 2**62), n, maxd) for _ in range(nl)]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190920 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
