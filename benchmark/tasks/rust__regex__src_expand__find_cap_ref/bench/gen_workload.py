"""Seeded workload generator for find_cap_ref (regex 1.0.0). Usage: python3 gen_workload.py <out_dir>

Line format (tab-separated), parsed by driver.rs:  <reps> <hex bytes of the replacement text>
<reps> = how many times the call is repeated on that case in time mode.
"""
import random, sys
from pathlib import Path

LITERALS = ["$foo", "${foo}", "$0", "$5", "$10", "$42a", "${42}a", "${42", "${42 ", " $0 ", "$", " ", "",
            "$$1", "$_", "${_x_}", "${}", "$}", "${", "$-1", "$1-$2", "$first_", "${first}_$second", "$007",
            "${007}", "$4294967295", "$4294967296", "${4294967296}", "$+1", "$ab cd", "${ab cd}", "x$foo",
            "$été", "$aé", "${a}}", "${{a}}", "$A_Z09z", "$1a${2}", "${42}}"]

NAME_CH = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
DIGITS = "0123456789"
TAILS = ["", " ", "}", "-", ".", "$x", " tail text", "é", "{", "$$"]

# size -> (n_cases, (min_name_len, max_name_len), reps)
SIZES = {"S": (150, (1, 12), 200), "M": (150, (60, 200), 200), "L": (150, (600, 2000), 600)}


def gen_case(rng, lo, hi):
    n = rng.randint(lo, hi)
    kind = rng.random()
    if kind < 0.3:
        name = "".join(rng.choice(DIGITS) for _ in range(n))          # numeric (may overflow u32)
    elif kind < 0.4:
        name = "".join(rng.choice(DIGITS) for _ in range(rng.randint(1, 9)))  # fits in u32
    else:
        name = "".join(rng.choice(NAME_CH) for _ in range(n))
    brace = rng.random() < 0.5
    close = (not brace) or rng.random() < 0.8
    s = "$" + ("{" if brace else "") + name + ("}" if brace and close else "")
    return s + rng.choice(TAILS)


def lines(size, rng):
    n, (lo, hi), reps = SIZES[size]
    cases = []
    if size == "S":
        cases += LITERALS
    cases += [gen_case(rng, lo, hi) for _ in range(n)]
    return ["%d\t%s" % (reps, c.encode("utf-8").hex()) for c in cases]


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20180502 + i)
        (out / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
