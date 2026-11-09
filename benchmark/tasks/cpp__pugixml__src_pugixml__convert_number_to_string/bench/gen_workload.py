"""Seeded workload generator for convert_number_to_string (pugixml). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines, parsed by driver.cpp:
  L <reps> <hex,hex,...>                  literal doubles, each as the 16-hex-digit IEEE-754 bit pattern
  O <reps> <hex,hex,...>                  same, but evaluated with an allocator that cannot allocate any memory (out-of-memory behaviour)
  G <reps> <seed> <n> <kind>              <n> doubles built by the driver (splitmix64)
<kind>: 0 random mantissa and exponent over the full range, 1 integers up to 2^60 (some negative), 2 decimals with up to 11 fractional digits,
        3 specials (NaN, +-Infinity, +-0, denormals) and values near powers of ten from 1e-300 to 1e300, 4 a mix of all four
"""
import random, struct, sys
from pathlib import Path


def bits(x):
    return "%016x" % struct.unpack("<Q", struct.pack("<d", x))[0]


LITERALS = [0.0, -0.0, 1.0, -1.0, 0.5, -0.5, 0.1, 0.25, 1.5, 2.0, 10.0, 100.0, 123456789.0, 1234567890123456.0, 12345678901234567.0, 0.000001,
            1e-7, 1.0000000000000002, 3.141592653589793, 2.718281828459045, 1e15, 1e16, 1e21, 1e22, 1e100, 1e300, 1.7976931348623157e308, 3.4028234663852886e38,
            2.2250738585072014e-308, 4.9406564584124654e-324, 9.999987484955998e-319, 1e-10, 12.375, 0.3, 0.7, 100.25, 65536.0, 4294967296.0, 9007199254740993.0,
            float("inf"), float("-inf"), float("nan"), 5e-324, 123.456, -987.654321, 1e-5, 0.00012345, 1e308, -1e308]

SIZES = {'S': (6, (20, 80), 1), 'M': (8, (5000, 20000), 4), 'L': (8, (60000, 200000), 1)}   # size -> (n_G_cases, (min_n, max_n), reps)


def lines(size, rng):
    n, (lo, hi), reps = SIZES[size]
    out = []
    if size == "S":
        for k in range(0, len(LITERALS), 5):
            out.append("L\t1\t%s" % ",".join(bits(x) for x in LITERALS[k:k + 5]))
        out.append("O\t1\t%s" % ",".join(bits(x) for x in [1.0, 0.5, float("nan"), float("inf"), float("-inf"), 0.0, 1e300, -123.456]))
    for i in range(n):
        out.append("G\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), rng.randint(lo, hi), i % 5))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190912 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
