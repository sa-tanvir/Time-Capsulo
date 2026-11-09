"""Seeded workload generator for fixed_handler::on_digit (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <item> TAB <item> ...   (reps = how many times the driver repeats the whole batch)
item = prefix,precision,digit,divisor,remainder,error,integral
  prefix:   digits already stored in the handler's buffer (size = len(prefix)); may be empty; may contain runs of 9
  precision, digit (one ASCII digit), divisor, remainder, error (uint64), integral (1/0)
Every item satisfies the preconditions of on_digit: remainder < divisor; for integral items error == 1 and divisor > 2;
otherwise (when the rounding check is reached) error < divisor.
Each item is an independent call on a fresh handler (fixed=true, exp10=0) whose buffer holds `prefix`; the driver records the
return value, the new size and the whole buffer (so the carry propagation is checked).
"""
import random, sys
from pathlib import Path


def item(rng):
    n = rng.choice([0, 1, 1, 2, 3, 5, 9, 15, 20])
    mode = rng.random()
    if mode < 0.35:
        prefix = "".join(rng.choice("0123456789") for _ in range(n))
    elif mode < 0.7:
        prefix = "".join("9" for _ in range(n))
    else:
        prefix = "".join(rng.choice("99999123") for _ in range(n))
    precision = max(0, n + 1 + rng.choice([-3, -1, 0, 0, 0, 0, 1, 2]))
    digit = rng.choice("0123456789" + "9" * 4)
    integral = rng.random() < 0.4
    if integral:
        divisor = rng.randrange(2 ** 33, 2 ** 62)
        error = 1
    else:
        divisor = rng.randrange(2 ** 20, 2 ** 63)
        error = rng.choice([1, rng.randrange(1, divisor // 20 + 2), rng.randrange(1, divisor // 3), rng.randrange(divisor // 3, divisor), divisor // 2, divisor - 1])
        error = min(error, divisor - 1)
    r = rng.random()
    if r < 0.3:
        remainder = rng.randrange(0, divisor)
    elif r < 0.5:
        remainder = max(0, min(divisor - 1, divisor // 2 + rng.randrange(-3, 4) * max(1, error)))
    elif r < 0.7:
        remainder = min(divisor - 1, rng.randrange(0, 3 * error + 2))
    elif r < 0.9:
        remainder = max(0, divisor - 1 - rng.randrange(0, 3 * error + 2))
    else:
        remainder = max(0, min(divisor - 1, divisor // 2 + rng.randrange(-2 * error - 2, 2 * error + 3)))
    return "%s,%d,%s,%d,%d,%d,%d" % (prefix, precision, digit, divisor, remainder, error, 1 if integral else 0)


def lines(size, rng):
    reps, ncase, per = {"S": (1, 12, 8), "M": (10, 20, 500), "L": (10, 20, 5000)}[size]
    return ["%d\t" % reps + "\t".join(item(rng) for _ in range(per)) for _ in range(ncase)]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191202 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
