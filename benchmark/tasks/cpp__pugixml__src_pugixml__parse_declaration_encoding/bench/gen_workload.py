"""Seeded workload generator for parse_declaration_encoding (pugixml). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines, parsed by driver.cpp:
  L <reps> <text>                  literal buffer content (escapes \\t \\n \\r \\\\ allowed); the function is called with size = len(text)
  G <reps> <seed> <padlen> <kind>  buffer built by the driver (splitmix64): `<?xml version="1.0"` + <padlen> filler characters (no '?', no 'n')
      + a tail chosen by <kind>: 0 valid encoding attribute (random quotes / spacing around '=' / name) followed by more text,
      1 no encoding attribute (declaration ends), 2 an "en" that is not "encoding" (enable=...), 3 unterminated encoding value,
      4 encoding without '=', 5 encoding value without an opening quote.
"""
import random, sys
from pathlib import Path

LITERALS = [
    "", "<", "<?xml", "<?xml ", "<?xml?>", "<?xml version='1.0'?>", "<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<?xml version='1.0' encoding='UTF-8'?><n/>",
    "<?xml encoding='latin1'?>", "<?xml encoding = 'ISO-8859-1' ?>", "<?xml\tencoding\t=\t\"windows-1252\"?>", "<?xml\nversion='1.0'\nencoding='x'?>",
    "<?xml version='1.0' encoding=''?>", "<?xml version='1.0' encoding=\"\"?>", "<?xml version='1.0' encoding='a-b_c:d.e9'?>", "<?xml version='1.0' encoding='a b'?>",
    "<?xml version='1.0' encoding=utf-8?>", "<?xml version='1.0' encoding 'utf-8'?>", "<?xml version='1.0' encoding='utf-8", "<?xml version='1.0' encoding='utf-8\"?>",
    "<?xml version='1.0' encoding=\"utf-8'?>", "<?xml version='1.0' encod", "<?xml version='1.0' en", "<?xml version='1.0' e", "<?xml version='1.0' enc",
    "<?xml version='1.0' enable='1' encoding='utf-8'?>", "<?xml version='1.0' ten encoding='utf-8'?>", "<?xml version='1.0' ?><?xml encoding='utf-8'?>",
    "<?xml version='1.0' standalone='yes' encoding='utf-8'?>", "<?xml version='1.0'? encoding='utf-8'?>", "<?xmlx encoding='utf-8'?>", "<?xml-stylesheet encoding='x'?>",
    "<?XML encoding='utf-8'?>", " <?xml encoding='utf-8'?>", "<?xml\x01encoding='utf-8'?>", "<?xml\rencoding='\u00e9'?>", "<?xml encoding='\u00e9\u00e8'?>", "<?xml encoding='a",
    "<?xml encoding='a'", "<?xml encoding=", "<?xml encoding= ", "<?xml encoding='a'?", "<?xml version='1.0' encoding='utf-8' encoding='latin1'?>",
    "<?xml version=\"1.0\" encoding=\"utf-8\" ?><root encoding='x'/>",
]

SIZES = {'S': (16, (0, 40), 1), 'M': (16, (20000, 60000), 20), 'L': (16, (1000000, 2500000), 8)}   # size -> (n_G_cases, (min_pad, max_pad), reps)


def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def lines(size, rng):
    n, (lo, hi), reps = SIZES[size]
    out = []
    if size == "S":
        out += ["L\t1\t%s" % esc(s) for s in LITERALS]
    for i in range(n):
        out.append("G\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), rng.randint(lo, hi), i % 6 if i % 2 else 0))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190912 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
