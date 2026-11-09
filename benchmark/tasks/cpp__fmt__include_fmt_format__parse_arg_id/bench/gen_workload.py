"""Seeded workload generator for parse_arg_id (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <string> TAB <string> ...  (non-empty strings; backslash escapes \\t \\n \\\\ allowed).
Every string is passed to parse_arg_id(begin, end, handler); the driver records the handler calls (or the error message
raised through on_error) and the returned offset.
S: hand-written edge cases (empty id, indices, leading zero, overflow, names, invalid starts); M/L: batches of mostly
valid ids followed by '}' or ':spec' (more and longer batches), with a few erroneous ones.
"""
import random, sys
from pathlib import Path

EDGE = ["}", ":", ":x", "0}", "0:", "1}", "7:>5", "10}", "123456:x", "2147483647}", "2147483648}", "99999999999}", "0", "12", "5x", "05}", "00}", "1 }",
        "a}", "abc:", "_x1}", "Name_9}", "z", "name", "a b", "A1b2:<", "x-y}", "$}", " }", "-1}", "{}", "9a}", "é}", "2147483647", "214748364}", "1}}",
        "w}", "arg_name_with_digits_0123456789}", "_}", "_", "Z0"]
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"


def valid(rng):
    k = rng.random()
    if k < 0.5:
        ident = str(rng.choice([0, 1, 2, 3, 9, 10, 25, 99, 1000, 54321, rng.randrange(0, 2 ** 31)]))
    else:
        ident = rng.choice(LETTERS) + "".join(rng.choice(LETTERS + "0123456789") for _ in range(rng.choice([0, 1, 3, 6, 12])))
    tail = rng.choice(["}", "}", ":", ":>10", ":*^7}", "}x"])
    return ident + tail


def bad(rng):
    return rng.choice(["x", "3 ", "-4}", "99999999999}", "01}", "?}", "7x}"])


def lines(size, rng):
    out = []
    if size == "S":
        for i in range(0, len(EDGE), 5):
            out.append("1\t" + "\t".join(EDGE[i:i + 5]))
        for _ in range(8):
            out.append("1\t" + "\t".join(valid(rng) for _ in range(8)))
        return out
    reps, ncase, per, nbad = {"M": (20, 20, 500, 5), "L": (10, 20, 5000, 5)}[size]
    for _ in range(ncase):
        strs = [valid(rng) for _ in range(per)]
        for _ in range(nbad):
            strs[rng.randrange(per)] = bad(rng)
        out.append("%d\t" % reps + "\t".join(strs))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191202 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
