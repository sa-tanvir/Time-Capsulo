"""Seeded workload generator (level_formatter::format). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. Line: width TAB side(l|r|c) TAB level(0..6). S: all combinations; M/L: more random cases.
"""
import random, sys
from pathlib import Path

SEED = 20190118   # release date of spdlog 1.3.1 as an int; size i uses SEED + i

def lines(size, rng):
    out = []
    if size == "S":
        for s in "lrc":
            for w in [0, 1, 4, 5, 6, 7, 8, 9, 10, 20]:
                for lv in range(7):
                    out.append("%d\t%s\t%d" % (w, s, lv))
    n = {"S": 100, "M": 30000, "L": 300000}[size]
    for _ in range(n):
        out.append("%d\t%s\t%d" % (rng.choice([0, 3, 5, 6, 7, 8, 9, 12, 16, 32, 64, 128, rng.randrange(0, 129)]), rng.choice("lrc"), rng.randrange(0, 7)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
