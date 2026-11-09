"""Seeded workload generator for strconv_comment (pugixml). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines, parsed by driver.cpp:
  L <reps> <endch> <text>                     literal buffer content = the text after "<!--" (escapes \\t \\n \\r \\\\ allowed);
                                              <endch> is the `endch` argument ("0" stands for '<')
  G <reps> <seed> <len> <cr_pct> <kind>       text built by the driver (splitmix64): about <len> bytes of letters, single '-', "--x" (never "-->"),
      '>' (never right after '-'), and <cr_pct> percent line breaks (\\r, \\r\\n or \\n); then a tail chosen by <kind>:
      0 "-->" followed by more text, 1 no terminator at all, 2 "--" then the end of the buffer with endch '>', 3 "--" then the end with endch 'x'
"""
import random, sys
from pathlib import Path

LITERALS = [
    ("0", ""), ("0", "-->"), ("0", " c -->rest"), ("0", "text-->"), ("0", "a\\rb\\r\\nc\\nd\\r\\r-->"), ("0", "\\r\\rval1\\rval2\\r\\nval3\\nval4\\r\\r-->"),
    ("0", "\\r\\n\\r\\n\\r\\n-->"), ("0", "-"), ("0", "->"), ("0", "-->x-->"), ("0", "a--b-->"), ("0", "a---->"), ("0", "a--->"), ("0", "a-->>"),
    ("0", "--"), ("0", "-- >"), ("0", "no end"), ("0", "no end\\r"), ("0", "x\\r"), ("0", "\\r"), ("0", "\\r\\n"),
    (">", "--"), (">", "abc--"), (">", "a\\r\\nb--"), (">", "a-"), (">", "-"), (">", "a--b--"), (">", "a-->b--"), (">", "\\r--"), (">", ""),
    ("x", "--"), ("x", "abc--"), ("x", "abc-->"), ("<", "abc--"),
    ("0", "<!-- nested <!-- -->"), ("0", "a - b -- c --- d ---- e -->f"), ("0", "\\r\\r\\r\\r"), ("0", "x" * 70 + "\\r\\n" + "y" * 70 + "-->"),
]

SIZES = {'S': (8, (10, 100), 1), 'M': (8, (20000, 80000), 4), 'L': (8, (1500000, 3000000), 1)}   # size -> (n_G_cases, (min_len, max_len), reps)


def lines(size, rng):
    n, (lo, hi), reps = SIZES[size]
    out = []
    if size == "S":
        out += ["L\t1\t%s\t%s" % (e, t) for e, t in LITERALS]
    for i in range(n):
        out.append("G\t%d\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), rng.randint(lo, hi), rng.choice([0, 1, 5, 20]), [0, 0, 2, 0, 1, 3, 0, 2][i % 8]))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190912 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
