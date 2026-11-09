"""Seeded workload generator for strconv_escape (pugixml). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines, parsed by driver.cpp:
  L <reps> <text>                             literal text (escapes \\t \\n \\r \\\\ allowed)
  G <reps> <seed> <ntokens> <invalid_pct>     text built by the driver (splitmix64): <ntokens> tokens, each a short run of plain
      characters followed by a valid entity (&amp; &lt; &gt; &quot; &apos;, decimal or hex character references up to U+FFFFFFFF
      in 1-4 byte UTF-8 classes) or, with probability <invalid_pct> percent, a malformed / truncated entity.
The driver feeds every '&' of the text to strconv_escape, as the parser does, and hashes the final buffer after the gap is flushed.
"""
import random, sys
from pathlib import Path

LITERALS = [
    "", "plain", "&amp;&lt;&gt;&quot;&apos;", "&#1;&#32;&#x20;", "&#/;&#01;&#2;&#3;&#4;&#5;&#6;&#7;&#8;&#9;&#:;&#a;&#A;&#XA;",
    "&#x/;&#x01;&#x2;&#x3;&#x4;&#x5;&#x6;&#x7;&#x8;&#x9;&#x:;&#x@;&#xA;&#xB;&#xC;&#xD;&#xE;&#xF;&#xG;&#x`;&#xa;&#xb;&#xc;&#xd;&#xe;&#xf;&#xg;",
    "&#1&#32;&#x1&#32;&#1-&#32;&#x1-&#32;", "&q&#32;&qu&#32;&quo&#32;&quot&#32;", "&a&#32;&ap&#32;&apo&#32;&apos&#32;",
    "&a&#32;&am&#32;&amp&#32;", "&l&#32;&lt&#32;", "&g&#32;&gt&#32;", "&#x03B3;&#x03b3;&#x24B62;", "&#x03g;&#ab;&quot",
    "&#;&#x;&;&#x-;&#-;", "&#x12", "&g", "&gt", "&l", "&lt", "&a", "&amp", "&apos", "&", "&&", "&&amp;&", "&amp&amp;", "&am&amp;",
    "&#38;&#x26;&#60;&#62;", "&#128;&#2047;&#2048;&#65535;&#65536;&#1114111;", "&#x7f;&#x80;&#x7ff;&#x800;&#xffff;&#x10000;&#x10FFFF;",
    "&#4294967295;&#x7FFFFFFF;&#x10FFFFF;", "a &lt; b &amp;&amp; c &gt; d", "x&#65;y&#x42;z&#67", "&#9;\\t&#10;\\n&#13;\\r",
    "&#00000000000000000065;&#x0000000000000000041;", "text &amp", "&#X41;&#xA;&xyz;&#1&", "&amp;&quot;&amp;&apos;&amp;",
]

SIZES = {'S': (12, (5, 60), 1, 1), 'M': (12, (5000, 20000), 25, 4), 'L': (12, (150000, 300000), 25, 1)}   # size -> (n_G_cases, (min_tokens, max_tokens), invalid_pct_max, reps)


def lines(size, rng):
    n, (lo, hi), inv, reps = SIZES[size]
    out = []
    if size == "S":
        out += ["L\t1\t%s" % s for s in LITERALS]
    for _ in range(n):
        out.append("G\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), rng.randint(lo, hi), rng.randint(0, inv)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190912 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
