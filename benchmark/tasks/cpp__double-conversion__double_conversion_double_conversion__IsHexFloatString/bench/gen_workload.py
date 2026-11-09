"""Seeded workload generator for IsHexFloatString (double-conversion). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines parsed by driver.cpp:
  L <reps> <sep> <junk> <wide> <string>     one literal call (sep = separator char code, 0 = none; wide = 1 passes 16-bit characters)
  G <reps> <seed> <n> <nd> <pad>            n generated strings (the text after "0x": mantissa digits, optional '.', 'p', optional sign, decimal
      exponent; valid and broken variants: missing/misplaced parts, bad characters, trailing spaces, trailing junk, separators).
"""
import random, sys
from pathlib import Path


LIT = ["1p0", "1P0", "1.p0", ".1p0", ".p0", "p0", "1", "1.", "1.0", "1p", "1p+", "1p-", "1p+1", "1p-1", "abcdefp12", "ABCDEFP12", "1.8p1", "1.8p1 ", "1.8p1  \\t",
       "1.8p1x", "1.8p1 x", "1.8p+x", "g1p1", "1gp1", "1p1p1", "1.2.3p1", "1_2p3", "1_.2p3", "1._2p3", "1p1_2", "1p_1", "_1p1", "1__2p1", "1_2_3.4_5p6_7",
       "0p0", "00p00", "1p01", "1p0x", "1p0 \\n", " 1p1", "1 p1", "1p 1", "f.fp-1022"]
SIZES = {"S": (60, 12, 4, 3), "M": (500, 120, 40, 4), "L": (200, 4000, 4000, 6)}   # n per line, nd, pad, lines


def lines(size, rng):
    n, nd, pad, nl = SIZES[size]
    out = []
    if size == "S":
        for s in LIT:
            for sep, junk, wide in [(0, 0, 0), (0, 1, 0), (95, 0, 0), (95, 1, 1)]:
                out.append("L\t1\t%d\t%d\t%d\t%s" % (sep, junk, wide, s))
    for _ in range(nl):
        out.append("G\t1\t%d\t%d\t%d\t%d" % (rng.randrange(1, 2**62), n, nd, pad))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190920 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
