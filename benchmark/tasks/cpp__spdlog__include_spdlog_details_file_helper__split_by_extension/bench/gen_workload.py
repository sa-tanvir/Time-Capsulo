"""Seeded workload generator (file_helper::split_by_extension). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. One path per line (no tabs). S: edge cases + short random paths; M/L: paths of ~10x / ~100x more characters.
"""
import random, sys
from pathlib import Path

SEED = 20190118   # release date of spdlog 1.3.1 as an int; size i uses SEED + i

EDGE = ["mylog.txt", ".mylog.txt", ".mylog", "/aaa/bb.d/mylog", "/aaa/bb.d/mylog.txt", "aaa/bbb/ccc/mylog.txt", "aaa/bbb/ccc/mylog.",
        "aaa/bbb/ccc/.mylog.txt", "/aaa/bbb/ccc/.mylog", "../mylog.txt", ".././mylog.txt", ".././mylog.txt/xxx", "/mylog.txt", "//mylog.txt",
        "x", ".", "..", "...", "a.", "a.b", ".a.", "a..b", "..txt", "/.", "/a.", "dir.d/", "dir.d/.", "dir/.hidden.", "a.b.c.d", "/", "//", "./", "x/.y.z", "a/b.c/d.e"]
ALPHA = "abcdefghijklmnopqrstuvwxyz0123456789_-"

def rnd_path(rng, target):
    out = []
    n = 0
    while n < target:
        r = rng.random()
        if r < 0.15:
            tok = "/"
        elif r < 0.35:
            tok = "."
        else:
            tok = "".join(rng.choice(ALPHA) for _ in range(rng.randrange(1, 9)))
        out.append(tok)
        n += len(tok)
    s = "".join(out)
    tail = rng.random()
    if tail < 0.3:
        s += "." + "".join(rng.choice(ALPHA) for _ in range(rng.randrange(1, 5)))
    elif tail < 0.4:
        s += "."
    elif tail < 0.5:
        s += "/" + "".join(rng.choice(ALPHA) for _ in range(rng.randrange(1, 5)))
    return s

def lines(size, rng):
    out = []
    if size == "S":
        out += EDGE
        for _ in range(250):
            out.append(rnd_path(rng, rng.randrange(1, 30)))
    elif size == "M":
        for _ in range(1500):
            out.append(rnd_path(rng, rng.randrange(100, 400)))
    else:
        for _ in range(1000):
            out.append(rnd_path(rng, rng.randrange(1000, 4000)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
