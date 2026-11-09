"""Seeded workload generator (scoped_pad constructor). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. Line: width TAB side(l|r|c) TAB wrapped_text_length. Width 0..128. S: edge cases; M/L: more cases.
"""
import random, sys
from pathlib import Path

SEED = 20190118   # release date of spdlog 1.3.1 as an int; size i uses SEED + i

def one(rng):
    w = rng.choice([0, 1, 2, 3, 8, 16, 64, 127, 128, rng.randrange(0, 129), rng.randrange(0, 129)])
    return "%d\t%s\t%d" % (w, rng.choice("lrc"), rng.choice([0, 1, 2, 3, rng.randrange(0, 140), rng.randrange(0, 40)]))

def lines(size, rng):
    out = []
    if size == "S":
        for s in "lrc":
            for w in [0, 1, 2, 3, 4, 5, 8, 9, 128]:
                for n in [0, 1, 2, 3, 4, 8, 9, 127, 128, 129]:
                    out.append("%d\t%s\t%d" % (w, s, n))
        out += [one(rng) for _ in range(100)]
    elif size == "M":
        out += [one(rng) for _ in range(30000)]
    else:
        out += [one(rng) for _ in range(300000)]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
