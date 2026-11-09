"""Seeded workload generator for textwrap::dedent. Usage: python3 gen_workload.py <out_dir>

One case per line: <reps> TAB <text>, where <text> is escaped (\\\\ \\t \\n \\r) and unescaped by driver.rs.
Texts are multi-line blocks sharing a common whitespace indent (spaces, tabs, NBSP, ideographic space),
with deeper-indented lines, blank and whitespace-only lines, CRLF endings, mismatching indents and
optional final newline. S also holds the literal cases from the test suite.
"""
import random, sys
from pathlib import Path

WS = [" ", " ", " ", "\t", "\u00a0", "\u3000"]
WORDS = ["foo", "bar", "baz", "lorem", "ipsum", "x", "Zero-cost", "abstractions.", "fn", "main()", "{", "}",
         "\u00fcber", "na\u00efve", "\u65e5\u672c", "\u2014", "a\tb", "let", "=", "42;"]
LITERALS = ["", "\n", "    foo\n  bar\n    baz\n", "    foo\n  bar\n   \n    baz\n",
            "      foo\n\n        bar\n          foo\n          bar\n          baz\n",
            "      foo\n \n        bar\n          foo\n          bar\n          baz\n",
            "\tfoo\n  bar\n", "\t\tfoo\n\t\t\tbar\n", "\t  \tfoo\n\t  \t\tbar\n", "\t  \tfoo\n\t    \tbar\n",
            "  foo\n    bar", "\n    1st line\n      2nd line\n    3rd line\n", "   ", "  \n  x", "x\n  y\n",
            "  a\r\n    b\r\n", "\n\n   \n", "  \u00a0x\n  \u00a0  y\n", " \t\n    z\n    w"]
SIZES = {"S": (60, (1, 12)), "M": (60, (60, 200)), "L": (60, (600, 2000))}


def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def text(rng, nlines):
    base = "".join(rng.choice(WS) for _ in range(rng.choice([0, 1, 2, 4, 4, 8, 12])))
    style = rng.random()
    nl = "\r\n" if rng.random() < 0.1 else "\n"
    out = []
    for _ in range(nlines):
        r = rng.random()
        if r < 0.08:
            out.append("")
        elif r < 0.14:
            if rng.random() < 0.6:
                out.append(base[:rng.randint(0, len(base))] + rng.choice(["", " ", "  "]))
            else:
                out.append("".join(rng.choice(WS) for _ in range(rng.randint(1, len(base) + 3))))
        elif r < 0.14 + (0.03 if style < 0.5 else 0.0):
            cut = rng.randint(0, len(base))
            out.append(base[:cut] + rng.choice(WS) + " ".join(rng.choice(WORDS) for _ in range(rng.randint(1, 6))))
        else:
            extra = "".join(rng.choice(WS) for _ in range(rng.choice([0, 0, 0, 2, 4, 1])))
            out.append(base + extra + " ".join(rng.choice(WORDS) for _ in range(rng.randint(1, 10))))
    s = nl.join(out)
    if rng.random() < 0.7:
        s += nl
    if rng.random() < 0.2:
        s = nl + s
    return s


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20181210 + i)
        n, (lo, hi) = SIZES[size]
        cases = list(LITERALS) if size == "S" else []
        cases += [text(rng, rng.randint(lo, hi)) for _ in range(n)]
        (out_dir / ("workload_%s.txt" % size)).write_text("".join("1\t%s\n" % esc(c) for c in cases), encoding="utf-8")
