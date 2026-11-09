"""Seeded workload generator (name_formatter::format). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. Line: width TAB side(l|r|c) TAB name_length TAB name_seed. The driver synthesises the name from (length, seed). Name length grows 10x/100x for M/L.
"""
import random, sys
from pathlib import Path

SEED = 20190118   # release date of spdlog 1.3.1 as an int; size i uses SEED + i

def one(rng, maxlen):
    w = rng.choice([0, 0, 1, 3, 8, 16, 32, 64, 128, rng.randrange(0, 129), rng.randrange(0, 129)])
    return "%d\t%s\t%d\t%d" % (w, rng.choice("lrc"), rng.choice([0, 1, 2, rng.randrange(0, maxlen + 1), rng.randrange(0, maxlen + 1)]), rng.randrange(1, 10**6))

def lines(size, rng):
    n, maxlen = {"S": (400, 20), "M": (6000, 200), "L": (20000, 2000)}[size]
    out = []
    if size == "S":
        for s in "lrc":
            for w in [0, 1, 4, 5, 9, 128]:
                for ln in [0, 1, 2, 3, 4, 5, 6, 10]:
                    out.append("%d\t%s\t%d\t%d" % (w, s, ln, rng.randrange(1, 1000)))
    out += [one(rng, maxlen) for _ in range(n)]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
