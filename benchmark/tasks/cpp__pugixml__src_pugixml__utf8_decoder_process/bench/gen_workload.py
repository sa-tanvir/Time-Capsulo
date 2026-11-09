"""Seeded workload generator for utf8_decoder::process (pugixml). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines, parsed by driver.cpp:
  L <reps> <trait> <align> <hexbytes>                         literal UTF-8 byte string
  G <reps> <seed> <trait> <align> <len> <ascii_pct> <mix>     bytes built by the driver (splitmix64): about <len> bytes made of
      ASCII runs (<ascii_pct> percent of the items) and 2/3/4-byte sequences; <mix> percent of the items are damaged
      (stray continuation bytes, truncated sequences, invalid lead bytes).
<trait>: 0 utf16_writer, 1 utf32_writer, 2 latin1_writer, 3 utf8_writer, 4 utf16_counter, 5 utf32_counter, 6 utf8_counter
<align>: the input pointer is offset by 0..3 bytes from the start of its buffer (alignment changes with it).
"""
import random, sys
from pathlib import Path

def h(s):
    return s.encode("utf-8", "surrogatepass").hex()

LITERALS = [
    "", "a", "plain ascii text, long enough to pass several four byte blocks 0123456789", "éèÿ", "ΔΩ กข", "€퟿￿",
    "\U00010000\U0010ffff \U00024b62", "mixed é € \U0001f600 end",
]
RAW = [  # hex strings that are not valid UTF-8
    "80", "bf", "c3", "e2", "e282", "f0", "f09f", "f09f98", "c0af", "c180", "e0 80 80".replace(" ", ""), "f8888888", "ff", "fe", "c328", "e282 28".replace(" ", ""),
    "f09f9828", "61 80 62 c3 63 e2 82 64 f0 9f 98 65".replace(" ", ""), "eda080 edb080".replace(" ", ""), "f4908080", "f7bfbfbf", "00 61 00".replace(" ", ""),
    "41 42 43 44 80 45 46 47 48 49".replace(" ", ""), "c3a9c3a9c3a9c3", "e282ace282ace282", "f09f98 80f09f9880".replace(" ", ""),
]

SIZES = {'S': (14, (20, 200), 1), 'M': (14, (20000, 80000), 2), 'L': (14, (1500000, 3000000), 1)}   # size -> (n_G_cases, (min_len, max_len), reps)


def lines(size, rng):
    n, (lo, hi), reps = SIZES[size]
    out = []
    if size == "S":
        for s in LITERALS:
            for trait in (0, 1, 2, 3, 4, 5, 6):
                out.append("L\t1\t%d\t%d\t%s" % (trait, rng.randrange(4), h(s)))
        for x in RAW:
            for trait in (0, 1, 2, 3, 6):
                out.append("L\t1\t%d\t%d\t%s" % (trait, rng.randrange(4), x))
    for i in range(n):
        mix = rng.choice([0, 0, 1, 5, 20])
        out.append("G\t%d\t%d\t%d\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), i % 7, rng.randrange(4), rng.randint(lo, hi),
                                                      rng.choice([0, 30, 60, 90, 99]), mix))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190912 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
