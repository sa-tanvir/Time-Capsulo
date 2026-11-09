"""Seeded workload generator for textwrap::Wrapper::fill. Usage: python3 gen_workload.py <out_dir>

One case per line: <reps> TAB <width|max> TAB <break_words 0|1> TAB <initial_indent> TAB <subsequent_indent> TAB <text>;
strings are escaped (\\\\ \\t \\n \\r) and unescaped by driver.rs, which builds a
Wrapper::new(width).initial_indent(..).subsequent_indent(..).break_words(..) per case.
Texts: words of varied length, hyphenated words, '--flags', non-breaking spaces/hyphens, wide (CJK/fullwidth)
characters, runs of spaces, embedded and trailing newlines. Cases with break_words=0 use ASCII-only words:
the 2018 wrapping code panics (byte index not on a char boundary) on some multibyte input with break_words(false). S also holds the literal cases from the tests.
"""
import random, sys
from pathlib import Path

WORDS = ["foo", "bar", "baz", "a", "x", "lorem", "ipsum", "dolor", "sit", "amet,", "consectetur", "adipiscing",
         "elit.", "Memory", "safety", "without", "garbage", "collection.", "Zero-cost", "abstractions.",
         "foo-bar-baz", "Na2-CH4", "--foo-bar", "foo(-)bar", "foo--bar", "trailing-", "Internationalization",
         "\u00fcber", "na\u00efve", "\u65e5\u672c\u8a9e", "\uff28\uff45\uff4c\uff4c\uff4f,", "\u2013", "foo\u00a0bar",
         "foo\u2011bar\u2011baz", "supercalifragilisticexpialidocious", "\u00e9t\u00e9", "1", "3", "5", "7"]
INDENTS = ["", "", "", "  ", "* ", ">>>", "    ", "\u2192 ", "\t"]
LITERALS = [(10, 1, "", "", "foo bar baz"), (11, 1, "", "", "test\n"), (11, 1, "", "", "test\n\na\n\n"),
            (7, 1, "", "", "1 3 5 7\n1 3 5 7"), (5, 1, "", "", "1 3 5 7\n1 3 5 7"), (5, 1, "", "", "ab\ncdefghijkl"),
            (5, 1, "", "", "abcdefgh\nijkl"), (5, 0, "", "", "foo\u00a0bar\u00a0baz"), (5, 0, "", "", "foo\u2011bar\u2011baz"),
            (10, 1, "!!!", "", ""), (10, 1, ">>>", "", "foo"), (15, 1, "", "", "Memory safety without garbage collection."),
            (6, 1, "* ", "  ", "foo bar baz"), (5, 1, "* ", "  ", "foobarbaz"), (0, 1, "", "", "foo bar"),
            ("max", 1, "", "", "foo bar"), (6, 1, "", "", "  foo bar"), (6, 1, "", "", "foo bar  "),
            (5, 1, "", "", "foo               bar"), (9, 1, "", "", "aaabbbccc x yyyzzzwww"), (1, 1, "", "", "x \u2013 x"),
            (15, 1, "", "", "\uff28\uff45\uff4c\uff4c\uff4f, \uff37\uff4f\uff52\uff4c\uff44!"), (5, 1, "", "", "foo-bar-baz"),
            (5, 0, "", "", "The --foo-bar flag."), (4, 0, "", "", "foo--bar"), (5, 0, "", "", "foobar-baz"),
            (9, 1, "", "", "foo-bar-baz"), (5, 0, "", "", "foobar-"), (5, 1, "", "", "\uff28\uff45\uff4c\uff4c\uff4f"),
            (3, 1, "", "", "\n"), (3, 1, "", "", "")]
SIZES = {"S": (40, (3, 40)), "M": (40, (300, 800)), "L": (40, (3000, 8000))}


def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


ASCII_WORDS = [w for w in WORDS if w.isascii()]


def text(rng, nwords, ascii_only):
    words = ASCII_WORDS if ascii_only else WORDS
    out = []
    for _ in range(nwords):
        out.append(rng.choice(words))
        r = rng.random()
        out.append("\n" if r < 0.03 else "\n\n" if r < 0.04 else "   " if r < 0.08 else " ")
    s = "".join(out)
    return s if rng.random() < 0.5 else s.rstrip(" ")


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20181210 + i)
        n, (lo, hi) = SIZES[size]
        cases = list(LITERALS) if size == "S" else []
        for _ in range(n):
            w = rng.choice([0, 1, 3, 5, 8, 10, 15, 20, 30, 40, 60, 72, 79, 80, 100, 120, "max"])
            brk = int(rng.random() < 0.75)
            cases.append((w, brk, rng.choice(INDENTS), rng.choice(INDENTS), text(rng, rng.randint(lo, hi), not brk)))
        (out_dir / ("workload_%s.txt" % size)).write_text(
            "".join("1\t%s\t%d\t%s\t%s\t%s\n" % (w, b, esc(ii), esc(si), esc(t)) for w, b, ii, si, t in cases),
            encoding="utf-8")
