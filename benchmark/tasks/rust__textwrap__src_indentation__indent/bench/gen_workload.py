"""Seeded workload generator for textwrap::indent. Usage: python3 gen_workload.py <out_dir>

One case per line: <reps> TAB <prefix> TAB <text>; prefix and text are escaped (\\\\ \\t \\n \\r) and
unescaped by driver.rs. Texts are multi-line blocks mixing indented/unindented lines, empty and
whitespace-only lines (spaces, tabs, NBSP, ideographic space), CRLF endings and optional final newline.
S also holds the literal cases from the test suite and docs.
"""
import random, sys
from pathlib import Path

WS = [" ", " ", " ", "\t", "\u00a0", "\u3000"]
WORDS = ["foo", "bar", "baz", "lorem", "ipsum", "x", "Zero-cost", "abstractions.", "fn", "main()", "{", "}",
         "\u00fcber", "na\u00efve", "\u65e5\u672c", "\u2014", "a\tb", "let", "=", "42;"]
PREFIXES = ["", "  ", "    ", "//", "> ", "\t", "->", "# ", "\u2192 ", "| ", "  * "]
LITERALS = [("\n", "  "), ("  foo\nbar\n  baz\n", "//"), ("  foo\nbar\n\n  baz\n", "//"), ("", "  "),
            ("\nFoo\nBar\n", "  "), ("\nFoo\n\nBar\n  \t\nBaz\n", "->"), (" \t  Foo   ", "->"), ("x", ""),
            ("a\r\nb\r\n", "> "), ("\n\n\n", "#"), ("   ", "->"), ("a\nb", "  "), ("\u00a0\n\u3000x\n", "| ")]
SIZES = {"S": (60, (1, 12)), "M": (60, (60, 200)), "L": (60, (600, 2000))}


def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def text(rng, nlines):
    nl = "\r\n" if rng.random() < 0.1 else "\n"
    out = []
    for _ in range(nlines):
        r = rng.random()
        if r < 0.1:
            out.append("")
        elif r < 0.18:
            out.append("".join(rng.choice(WS) for _ in range(rng.randint(1, 6))))
        else:
            ind = "".join(rng.choice(WS) for _ in range(rng.choice([0, 0, 2, 4, 8, 1])))
            out.append(ind + " ".join(rng.choice(WORDS) for _ in range(rng.randint(1, 10))))
    s = nl.join(out)
    if rng.random() < 0.7:
        s += nl
    return s


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20181210 + i)
        n, (lo, hi) = SIZES[size]
        cases = list(LITERALS) if size == "S" else []
        cases += [(text(rng, rng.randint(lo, hi)), rng.choice(PREFIXES)) for _ in range(n)]
        (out_dir / ("workload_%s.txt" % size)).write_text(
            "".join("1\t%s\t%s\n" % (esc(p), esc(t)) for t, p in cases), encoding="utf-8")
