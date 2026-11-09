"""Seeded workload generator for text_output_escaped (pugixml). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines, parsed by driver.cpp:
  L <reps> <type> <flags> <text>                      literal text (escapes \\t \\n \\r \\\\ and \\xHH allowed)
  G <reps> <seed> <type> <flags> <len> <special_pct>  text built by the driver (splitmix64): about <len> bytes of plain ASCII runs and a few
      multi-byte UTF-8 characters, where <special_pct> percent of the items are one of & < > " ' or a control character 1..31.
<type>: 0 = ctx_special_pcdata (element text), 1 = ctx_special_attr (attribute value)
<flags>: bit mask of format_skip_control_chars (0x100) and format_attribute_single_quote (0x200)
"""
import random, sys
from pathlib import Path

LITERALS = [
    "", "plain text", "<>'\"&\\x04\\r\\n\\t", "&&&&", "<<<>>>", "\"\"''", "a&b<c>d\"e'f", "\\x01\\x02\\x1f\\x1e\\x08\\x0b\\x0c\\x7f", "\\t\\n\\r\\t\\n\\r",
    "\u00e9\u20ac\U0001f600", "&amp; &lt; already escaped &#04;", "x" * 40 + "&" + "y" * 40,
    "end", "a\\x03b\\x03c", "'single' \"double\"", ">]]>", "<![CDATA[x]]>", "\\n", "&",
]

SIZES = {'S': (16, (10, 80), 30, 1), 'M': (16, (20000, 80000), 10, 8), 'L': (16, (1500000, 4000000), 5, 1)}   # size -> (n_G_cases, (min_len, max_len), max_special_pct, reps)


def lines(size, rng):
    n, (lo, hi), pct, reps = SIZES[size]
    out = []
    if size == "S":
        for s in LITERALS:
            for typ in (0, 1):
                for flags in (0, 0x100, 0x200):
                    out.append("L\t1\t%d\t%d\t%s" % (typ, flags, s))
    for i in range(n):
        out.append("G\t%d\t%d\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), i % 2, rng.choice([0, 0, 0x100, 0x200, 0x300]),
                                                  rng.randint(lo, hi), rng.choice([0, 1, 3, pct])))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190912 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
