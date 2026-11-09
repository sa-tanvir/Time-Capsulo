"""Seeded workload generator (pattern_formatter::handle_padspec_). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. Line: "p" TAB text (the text may be empty). Each text is passed whole to the function. Digit runs have at most 18 significant digits; M/L add long runs of leading zeros (10x / 100x longer).
"""
import random, sys
from pathlib import Path

SEED = 20190118   # release date of spdlog 1.3.1 as an int; size i uses SEED + i

EDGE = ["", "-", "=", "5", "-5", "=5", "05", "-05", "5x", "-5x", "=5x", "12ab", "128", "129", "300", "-300", "=300", "x", "-x", "=x", "--5", "-=5", "==5", "-", "=-", "%v", "8l", "-8l", "=8l",
        "999999", "1000000000000000000", "-0", "=0", "0", "00", " 5", "5 ", "-12345678901234567", "=127", "127", "128abc", "- 5", "9"]
def one(rng, zeros):
    r = rng.random()
    pre = "" if r < 0.4 else rng.choice("-=") if r < 0.9 else rng.choice("x%!")
    if rng.random() < 0.8:
        digits = "0" * rng.randrange(0, zeros + 1) + str(rng.choice([rng.randrange(0, 20), rng.randrange(0, 300), rng.randrange(0, 10**6)]))
    else:
        digits = ""
    tail = "".join(rng.choice("abcxyzv%!-=5") for _ in range(rng.randrange(0, 6)))
    return "p\t" + pre + digits + tail

def lines(size, rng):
    zeros, n = {"S": (1, 300), "M": (200, 5000), "L": (2000, 5000)}[size]
    out = []
    if size == "S":
        out += ["p\t" + e for e in EDGE]
    out += [one(rng, zeros) for _ in range(n)]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
