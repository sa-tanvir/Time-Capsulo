"""Seeded workload generator for parse_chrono_format (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <string> TAB <string> ...  (non-empty strings; backslash escapes \\t \\n \\\\ allowed).
Every string is passed to parse_chrono_format(begin, end, handler); the driver records every handler callback (with the text
chunks) and the returned offset, or the message of the format_error that was thrown.
S: hand-written edge cases (every conversion, E/O modifiers, %%, %n, %t, stop at '}', invalid input); M/L: batches of
random valid format strings of growing length (and a few strings terminated by '}').
"""
import random, sys
from pathlib import Path

PLAIN = ["%a", "%A", "%w", "%u", "%b", "%B", "%H", "%I", "%M", "%S", "%c", "%x", "%X", "%D", "%F", "%r", "%R", "%T", "%p", "%Q", "%q", "%z", "%Z",
         "%Ec", "%Ex", "%EX", "%Ow", "%Ou", "%OH", "%OI", "%OM", "%OS", "%%", "%n", "%t"]
EDGE = ["%H:%M:%S", "abc", "%", "a%", "%%%", "%Y", "%E", "%Ey", "%O", "%Oz", "%Ea", "}", "%H}", "ab}cd", "x%Hy}z%M", "%}", "%H%", "  %S  ", "%H%M%S%Q%q",
        "t=%Q%q", "%%H", "%n%t", "text only no spec", "%EcX%OS", "%-H", "%5H", "%Ec%Ex%EX", "{%H}", "%a %A %b %B", "}%H"]
WORDS = ["time", " ", ":", "-", "/", "T", "at ", "dur=", "(", ")", ", ", "x"]


def rnd(rng, nparts):
    out = []
    for _ in range(nparts):
        out.append(rng.choice(PLAIN) if rng.random() < 0.55 else rng.choice(WORDS))
    return "".join(out)


def lines(size, rng):
    out = []
    if size == "S":
        for i in range(0, len(EDGE), 6):
            out.append("1\t" + "\t".join(EDGE[i:i + 6]))
        out.append("1\t" + "\t".join(PLAIN))
        for _ in range(8):
            out.append("1\t" + "\t".join(rnd(rng, rng.randrange(1, 12)) for _ in range(6)))
        return out
    reps, ncase, per, parts = {"M": (10, 20, 100, 30), "L": (5, 20, 1000, 100)}[size]
    for _ in range(ncase):
        strs = [rnd(rng, rng.randrange(1, parts)) for _ in range(per)]
        for _ in range(per // 100):
            strs[rng.randrange(per)] = rnd(rng, 5) + "}" + rnd(rng, 3)
        out.append("%d\t" % reps + "\t".join(strs))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191202 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
