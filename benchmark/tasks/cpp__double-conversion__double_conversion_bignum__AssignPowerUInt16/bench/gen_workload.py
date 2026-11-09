"""Seeded workload generator for Bignum::AssignPowerUInt16 (double-conversion). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines: <reps> TAB "base exp base exp ..." (pairs). Every pair is one call AssignPowerUInt16(base, exp).
The result stays below 2^MAXBITS (S 64, M 800, L 3400) and bit_length(odd part of base) * exp <= 3300 (library capacity).
"""
import random, sys
from pathlib import Path


SIZES = {"S": (64, 120, 1), "M": (800, 400, 6), "L": (3400, 400, 8)}   # maxbits, pairs per line, lines
BASES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 12, 16, 25, 32, 100, 1000, 1024, 65535, 65534, 32768, 49152, 40000, 255, 257, 65521]


def ok(b, e, maxbits):
    odd = b
    while odd % 2 == 0:
        odd //= 2
    return (b ** e).bit_length() <= maxbits and odd.bit_length() * e <= 3300


def pair(rng, maxbits):
    while True:
        r = rng.random()
        b = rng.choice(BASES) if r < 0.6 else rng.randint(1, 65535)
        if b == 1:
            e = rng.randint(0, 5000)
        else:
            lim = int(maxbits / max(0.5, __import__("math").log2(b)))
            e = rng.randint(0, max(0, lim)) if rng.random() < 0.5 else rng.randint(max(0, lim * 3 // 4), max(0, lim))
        if ok(b, e, maxbits):
            return b, e


def lines(size, rng):
    maxbits, n, nl = SIZES[size]
    out = []
    if size == "S":
        pairs = [(10, 0), (10, 1), (10, 2), (1, 7), (2, 0), (2, 1), (2, 10), (3, 5), (3, 40), (7, 20), (65535, 4), (65535, 1), (16, 15), (5, 27), (10, 19)]
        out.append("1\t" + " ".join("%d %d" % p for p in pairs))
    for _ in range(nl):
        out.append("1\t" + " ".join("%d %d" % pair(rng, maxbits) for _ in range(n)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190920 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
