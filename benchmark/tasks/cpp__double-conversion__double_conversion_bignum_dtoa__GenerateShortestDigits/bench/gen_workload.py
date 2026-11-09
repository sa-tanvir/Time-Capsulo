"""Seeded workload generator for GenerateShortestDigits (double-conversion). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines: <reps> <seed> <n> <emin> <emax> <single>.  The driver draws n positive finite numbers (binary exponent in
[emin, emax], mantissas: powers of two, small, all-ones, random), sets up numerator/denominator/delta_minus/delta_plus exactly as the
shortest mode of the library does, and calls GenerateShortestDigits on each. single=1 uses binary32 values.
"""
import random, sys
from pathlib import Path


SIZES = {"S": [(-20, 20, 0, 200), (-8, 8, 1, 200)], "M": [(-200, 200, 0, 500), (-100, 100, 1, 500)], "L": [(-1074, 1023, 0, 800), (-149, 127, 1, 800)]}


def lines(size, rng):
    out = []
    for emin, emax, single, n in SIZES[size]:
        for _ in range(3 if size != "S" else 2):
            out.append("1\t%d\t%d\t%d\t%d\t%d" % (rng.randrange(1, 2**62), n, emin, emax, single))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190920 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
