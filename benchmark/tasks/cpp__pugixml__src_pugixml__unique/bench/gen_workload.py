"""Seeded workload generator for unique (pugixml). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines, parsed by driver.cpp:
  L <reps> <type> <v1,v2,...>                    literal array of ints (equal values adjacent)
  G <reps> <seed> <type> <n> <maxrun> <mode>     array of <n> ints built by the driver (splitmix64): runs of equal values with a run
      length drawn from 1..<maxrun>, values strictly increasing between runs.
<type>: 0 = int; 1 = struct {a, b} with b derived from a (equality compares both fields)
<mode>: 0 plain runs, 2 long first run, 3 one single run covering the array, 4 the last two elements equal
"""
import random, sys
from pathlib import Path

LITERALS = [
    [], [1], [1, 1], [1, 2], [1, 1, 2], [1, 2, 2], [1, 1, 1, 1], [1, 2, 3, 4, 5], [1, 1, 2, 2, 3, 3], [1, 2, 2, 2, 3], [0, 0, 0, 1, 2, 3],
    [1, 2, 3, 3], [1, 2, 3, 4, 4], [5, 5, 5, 5, 5, 6], [-1, -1, 0, 0, 1, 1], [1, 1, 2, 3, 3, 3, 4, 5, 5, 6, 7, 7, 7, 7, 8],
    [1, 2, 1, 2], [3, 3, 1, 1, 2],   # unsorted but only adjacent duplicates are removed
]

SIZES = {'S': (24, (0, 200), 1), 'M': (24, (20000, 120000), 4), 'L': (24, (1000000, 3000000), 1)}   # size -> (n_G_cases, (min_n, max_n), reps)


def lines(size, rng):
    n, (lo, hi), reps = SIZES[size]
    out = []
    if size == "S":
        for vals in LITERALS:
            for typ in (0, 1):
                out.append("L\t1\t%d\t%s" % (typ, ",".join(map(str, vals))))
    for i in range(n):
        out.append("G\t%d\t%d\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), i % 2, rng.randint(lo, hi),
                                                  rng.choice([1, 1, 2, 3, 8, 50]), rng.choice([0, 0, 0, 2, 3, 4])))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190912 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
