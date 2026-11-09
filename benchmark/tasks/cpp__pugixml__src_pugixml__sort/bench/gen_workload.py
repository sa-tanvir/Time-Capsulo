"""Seeded workload generator for sort (pugixml). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines, parsed by driver.cpp:
  L <reps> <type> <v1,v2,...>             literal array of ints
  G <reps> <seed> <type> <n> <pattern>    array of <n> ints built by the driver (splitmix64)
<type>: 0 = int, ascending (impl::less); 1 = int, descending (predicate a > b);
        2 = struct {key, id}: sorted by key, then by the unique id (a total order, so the result is unique)
<pattern>: 0 random, 1 ascending, 2 descending, 3 all equal, 4 eight distinct values, 5 sawtooth (i mod 1000),
           6 nearly sorted (1% random swaps), 7 random with many duplicates (n/10 distinct values)
"""
import random, sys
from pathlib import Path

LITERALS = [
    [], [1], [2, 1], [1, 2], [3, 1, 2], [1, 1, 1], [5, 4, 3, 2, 1], [1, 2, 3, 4, 5], [2, 2, 1, 1, 3, 3], [0, -1, 1, -2, 2, -3, 3],
    list(range(16, 0, -1)), list(range(17, 0, -1)), [i % 3 for i in range(17)], [(i * 7919) % 101 for i in range(40)],
    [2147483647, -2147483648, 0, 2147483647, -2147483648], [(i * 31) % 17 for i in range(100)],
]

SIZES = {'S': (24, (0, 300), 1), 'M': (24, (10000, 60000), 3), 'L': (24, (200000, 700000), 1)}   # size -> (n_G_cases, (min_n, max_n), reps)


def lines(size, rng):
    n, (lo, hi), reps = SIZES[size]
    out = []
    if size == "S":
        for vals in LITERALS:
            for typ in (0, 1, 2):
                out.append("L\t1\t%d\t%s" % (typ, ",".join(map(str, vals))))
    for i in range(n):
        out.append("G\t%d\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), i % 3, rng.randint(lo, hi), i % 8))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190912 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
