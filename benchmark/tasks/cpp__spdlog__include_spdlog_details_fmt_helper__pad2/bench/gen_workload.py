"""Seeded workload generator (fmt_helper::pad2). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. One int per line. S: values around the 0/9/10/99/100 boundaries and negatives; M/L: more random values over a wider range (incl. int limits in L).
"""
import random, sys
from pathlib import Path

SEED = 20190118   # release date of spdlog 1.3.1 as an int; size i uses SEED + i

def lines(size, rng):
    out = []
    if size == "S":
        out += [str(v) for v in list(range(-12, 125)) + [999, 1000, 9999, -99, -100, -1000, 2147483647, -2147483648]]
        out += [str(rng.randrange(-5000, 5000)) for _ in range(300)]
    elif size == "M":
        out += [str(rng.choice([rng.randrange(-20, 130), rng.randrange(-10**6, 10**7)])) for _ in range(30000)]
    else:
        out += [str(rng.choice([rng.randrange(-20, 130), rng.randrange(-2**31, 2**31)])) for _ in range(300000)]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
