"""Seeded workload generator (fmt_helper::pad_uint). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. Line: type(0=unsigned short,1=uint32,2=uint64) TAB value TAB width. Widths 0..20. S: boundary cases; M/L: more cases with wider values.
"""
import random, sys
from pathlib import Path

SEED = 20190118   # release date of spdlog 1.3.1 as an int; size i uses SEED + i

MAXV = {0: 65535, 1: 2**32 - 1, 2: 2**64 - 1}
def one(rng, big):
    t = rng.randrange(0, 3)
    bits = rng.randrange(0, {0: 17, 1: 33, 2: 65}[t])
    v = rng.randrange(0, 2 ** bits) if bits else 0
    v = min(v, MAXV[t])
    if not big and rng.random() < 0.5:
        v = rng.randrange(0, 1000)
    return "%d\t%d\t%d" % (t, v, rng.randrange(0, 21))

def lines(size, rng):
    out = []
    if size == "S":
        for t in range(3):
            for v in [0, 1, 9, 10, 99, 100, 12345, MAXV[t]]:
                for w in [0, 1, 3, 6, 9, 10, 20]:
                    out.append("%d\t%d\t%d" % (t, v, w))
        out += [one(rng, False) for _ in range(150)]
    elif size == "M":
        out += [one(rng, True) for _ in range(30000)]
    else:
        out += [one(rng, True) for _ in range(300000)]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
