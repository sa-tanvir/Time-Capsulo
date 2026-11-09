"""Seeded workload generator for bigint::compare (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <token> TAB <token> ...
Tokens define a pool of non-negative big integers (in order) and then the pairs to compare:
  t:k:m     bigint with value 10^k * m   (assign_pow10(k), then *= m; m odd)
  n:v       bigint(v), v a 64-bit integer whose lowest 32 bits are not 0 (or v < 2^32)
  s:v:sh    bigint(v) <<= sh, v odd and < 2^32
  c:i,j     compare pool[i] with pool[j]
All pool values are "normalised" as library operations produce them (the lowest stored 32-bit digit is not zero, except for the number 0),
and all fit in the 32-digit inline storage of a bigint (about 2^1000).
The driver records only the sign of compare(pool[i], pool[j]); for such normalised numbers it is the numeric order (value() below gives the
exact integer of every token).
S: handcrafted numbers (zero, equal values, shifts by whole digits, values 2^32 apart); M/L: batches of random numbers, 25% equal pairs.
"""
import random, sys
from pathlib import Path


def value(tok):
    p = tok.split(":")
    if p[0] == "t":
        return 10 ** int(p[1]) * int(p[2])
    if p[0] == "n":
        return int(p[1])
    return int(p[1]) << int(p[2])


def rnd_token(rng, kmax):
    r = rng.random()
    if r < 0.6:
        return "t:%d:%d" % (rng.randrange(0, kmax), rng.choice([1, 1, 3, 5, 7, 99, 12345, 2 ** 31 - 1]))
    if r < 0.8:
        v = rng.randrange(0, 2 ** rng.choice([8, 31, 40, 63]))
        if v >= 2 ** 32 and v % 2 ** 32 == 0:
            v += 1
        return "n:%d" % v
    return "s:%d:%d" % (rng.choice([1, 3, 7, 12345, 2 ** 31 - 1]), rng.randrange(0, 31 * 32))


def lines(size, rng):
    kmax, pool_n, npairs, reps = {"S": (40, 12, 30, 1), "M": (120, 100, 3000, 20), "L": (270, 200, 20000, 20)}[size]
    out = []
    ncase = 4 if size == "S" else 10
    for ci in range(ncase):
        toks = [rnd_token(rng, kmax) for _ in range(pool_n)]
        if size == "S" and ci == 0:
            toks = ["n:0", "n:1", "n:42", "n:43", "s:42:32", "n:%d" % (42 * 0x100000001), "n:4294967295", "n:4294967297", "s:1:32", "s:1:64", "s:1:96", "t:0:1"]
        line = ["%d" % reps] + toks
        for _ in range(npairs):
            i = rng.randrange(len(toks))
            j = i if rng.random() < 0.25 else rng.randrange(len(toks))
            line.append("c:%d,%d" % (i, j))
        out.append("\t".join(line))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191202 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
