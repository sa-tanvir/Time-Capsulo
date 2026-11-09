"""Seeded workload generator for parse_align (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <string> TAB <string> ...  (strings are non-empty; \\t \\n \\\\ escapes allowed).
Every string is passed to parse_align(begin, end, handler); the driver records the callbacks and the returned offset.
S: hand-written edge cases; M/L: batches of random strings over the alphabet below (more and longer batches).
"""
import random, sys
from pathlib import Path

EDGE = ["<", ">", "^", "=", "x", "*<", "*>", "*^", "*=", "{<", "{>", "{^", "{=", "{", "<<", "<>", ">>", "^^", "==", "x<y", "<x", "<5", ">10", "^.3f",
        "*<5", "0>8", "-^20", " <3", "ab", "abc", "x1", "xx<", "<}", "}<", "}>", ">}", "{x", "<{", "z=10", "a", "\\t<", "9", "9>", ":<", "=<", "<=", "^>"]
ALPHA = "<>^=*{} 0123456789abx.-:"
SIZES = {"S": (1, 1, 6), "M": (40, 4000, 60), "L": (40, 40000, 400)}   # size -> (reps, batches-or-unused, batch size)


def rnd_str(rng):
    n = rng.choice([1, 1, 2, 2, 2, 3, 4, 6, 10])
    return "".join(rng.choice(ALPHA) for _ in range(n))


def lines(size, rng):
    out = []
    if size == "S":
        for i in range(0, len(EDGE), 6):
            out.append("1\t" + "\t".join(EDGE[i:i + 6]))
        for _ in range(10):
            out.append("1\t" + "\t".join(rnd_str(rng) for _ in range(8)))
        return out
    reps, ncase, per = {"M": (20, 20, 500), "L": (10, 20, 5000)}[size]
    for _ in range(ncase):
        out.append("%d\t" % reps + "\t".join(rnd_str(rng) for _ in range(per)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191202 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
