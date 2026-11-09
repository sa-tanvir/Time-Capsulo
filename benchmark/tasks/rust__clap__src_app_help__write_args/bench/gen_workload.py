"""Seeded workload generator for Help::write_args (clap). Usage: python3 gen_workload.py <out_dir>

One case per line (tab-separated), expanded deterministically by driver.rs:
  <which> <term_w> <n_flags> <n_opts> <n_pos> <hidden_pct> <seed>
which: 0 = flags followed by options (as for unified help), 1 = flags only, 2 = options only, 3 = positionals.
term_w: help width (0 = unlimited). hidden_pct: percentage of hidden arguments (some hidden ones also get
NextLineHelp, which keeps them visible). The driver (xorshift seeded with <seed>) gives each argument a unique
name, long/short switches, help text, an optional display order 0-4 (else default 999), value names, possible
values, defaults and NextLineHelp.
"""
import random, sys
from pathlib import Path

LITERALS = [
    "0\t120\t0\t0\t0\t0\t1", "1\t120\t1\t0\t0\t0\t2", "1\t120\t3\t0\t0\t0\t3", "2\t120\t0\t3\t0\t0\t4",
    "0\t120\t3\t3\t0\t0\t5", "3\t120\t0\t0\t3\t0\t6", "0\t120\t3\t3\t0\t100\t7", "3\t120\t0\t0\t4\t50\t8",
    "0\t60\t4\t4\t0\t20\t9", "0\t0\t5\t5\t0\t0\t10", "1\t120\t6\t0\t0\t30\t11", "2\t80\t0\t6\t0\t0\t12",
]
SIZES = {"S": (40, 1, 8), "M": (40, 30, 300), "L": (40, 300, 3000)}


def case(rng, lo, hi):
    which = rng.randrange(4)
    n = [rng.randint(lo, hi) for _ in range(3)]
    return "\t".join(str(x) for x in [which, rng.choice([0, 80, 120, 120, 200])] + n +
                     [rng.choice([0, 0, 10, 30]), rng.randrange(1, 2 ** 31)])


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20180214 + i)
        n, lo, hi = SIZES[size]
        lines = list(LITERALS) if size == "S" else []
        lines += [case(rng, lo, hi) for _ in range(n)]
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n", encoding="utf-8")
