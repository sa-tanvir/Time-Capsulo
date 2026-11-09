"""Seeded workload generator for string_to_integer (pugixml). Usage: python3 gen_workload.py <out_dir>

Tab-separated lines, parsed by driver.cpp (in L lines the string uses the escapes \\t \\n \\r \\\\):
  L <reps> <type> <string>                  literal input
  G <reps> <seed> <type> <len> <kind>       input expanded by the driver (splitmix64) from the seed
<type>: 0 = int (min INT_MIN, max INT_MAX), 1 = unsigned int, 2 = long long, 3 = unsigned long long
        (all four are instantiations of string_to_integer<unsigned T>), 4 = run all four.
<kind> (shape of the string, <len> = number of digits / leading zeros / whitespace):
  0 random decimal digits, 1 0x-prefixed hex digits, 2 <len> leading zeros + 1-19 digit number,
  3 negative decimal digits, 4 negative hex with <len> leading zeros, 5 whitespace + optional '+' + zeros + number + junk
"""
import random, sys
from pathlib import Path

LITERALS = [
    "", " ", "0", "1", "-0", "+0", "+1", "-1", "  \t\n\r 42", "0777", "00012", "12abc", "1e5", "+-1", "- 1", "+ 1", "--1", "abc",
    "0x", "0X", "0x0", "0xFf", "0XfF", "+0xa", "-0x20", "-0x1", "0x5ab", "0xzz", "0x1G", "0x 1", "0x-1", "-0x", "0Xg",
    "127", "2147483647", "2147483648", "-2147483647", "-2147483648", "-2147483649", "-4294967296", "4294967295",
    "4294967296", "5294967295", "21474836479", "0x7fffffff", "0x80000000", "-0x80000000", "-0x80000001", "0xFFFFFFFF",
    "0x100000000", "0x123456789", "9223372036854775807", "9223372036854775808", "-9223372036854775808",
    "-9223372036854775809", "-18446744073709551616", "18446744073709551615", "18446744073709551616",
    "28446744073709551615", "166020696663385964543", "0x7FFFFFFFFFFFFFFF", "0x8000000000000000", "-0x8000000000000000",
    "-0x8000000000000001", "0xFFFFFFFFFFFFFFFF", "0x10000000000000000", "0xFFFFFFFFFFFFFFFFF",
    "0000000000000000000000000000000000000000000000001", "0x0000000000000000000000000000000000000000000000001",
    "4200000000", "4999999999", "4300000000", "1844674407370955161", "19000000000000000000", "10000000000000000000",
    "  -2147483648  ", "\t+7", "7\t8",
]

SIZES = {'S': (40, (3, 40), 1), 'M': (40, (10000, 50000), 4), 'L': (60, (500000, 1500000), 1)}   # size -> (n_cases, (min_len, max_len), reps)


def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def lines(size, rng):
    n, (lo, hi), reps = SIZES[size]
    out = []
    if size == "S":
        out += ["L\t1\t4\t%s" % esc(s) for s in LITERALS]
    for i in range(n):
        out.append("G\t%d\t%d\t%d\t%d\t%d" % (reps, rng.randrange(1, 2**62), rng.choice([0, 1, 2, 3, 4]),
                                            rng.randint(lo, hi), rng.choice([0, 1, 2, 3, 4, 5])))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20190912 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
