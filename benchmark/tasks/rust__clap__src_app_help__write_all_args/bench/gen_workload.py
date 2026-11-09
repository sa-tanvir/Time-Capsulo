"""Seeded workload generator for Help::write_all_args (clap). Usage: python3 gen_workload.py <out_dir>

One App per line (tab-separated), expanded deterministically by driver.rs:
  <unified> <term_w> <n_flags> <n_opts> <n_pos> <n_subcmds> <hidden_pct> <help_sc> <seed>
unified: 1 = AppSettings::UnifiedHelpMessage. term_w: help width (0 = unlimited). hidden_pct: percentage of
arguments / subcommands marked hidden (each element decided by the driver's xorshift PRNG seeded with <seed>).
help_sc: 1 = also add a subcommand literally named "help" (never counts as a visible subcommand).
The driver gives every element a name, long/short switch, help text, display order and optional value names /
possible values / NextLineHelp, all derived from <seed>.
"""
import random, sys
from pathlib import Path

LITERALS = [
    "0\t120\t0\t0\t0\t0\t0\t0\t1",
    "0\t120\t3\t0\t0\t0\t0\t0\t2",
    "0\t120\t0\t3\t0\t0\t0\t0\t3",
    "0\t120\t0\t0\t3\t0\t0\t0\t4",
    "0\t120\t0\t0\t0\t3\t0\t0\t5",
    "0\t120\t0\t0\t0\t0\t0\t1\t6",
    "0\t120\t2\t2\t2\t2\t0\t1\t7",
    "1\t120\t2\t2\t2\t2\t0\t0\t8",
    "1\t120\t2\t0\t0\t0\t0\t0\t9",
    "1\t120\t0\t2\t1\t0\t0\t0\t10",
    "1\t120\t0\t0\t2\t1\t0\t0\t11",
    "0\t120\t3\t3\t3\t3\t100\t0\t12",
    "0\t80\t4\t4\t2\t2\t50\t1\t13",
    "0\t0\t4\t4\t2\t2\t30\t0\t14",
    "1\t60\t5\t5\t5\t5\t20\t1\t15",
    "0\t120\t0\t0\t3\t0\t100\t0\t16",
]
SIZES = {"S": (40, 1, 8), "M": (40, 10, 80), "L": (80, 100, 800)}


def case(rng, lo, hi):
    unified = "1" if rng.random() < 0.4 else "0"
    term_w = str(rng.choice([0, 80, 100, 120, 120, 200]))
    counts = [str(rng.choice([0, rng.randint(lo, hi), rng.randint(lo, hi)])) for _ in range(4)]
    return "\t".join([unified, term_w] + counts + [str(rng.choice([0, 0, 10, 30])), str(rng.randrange(2)),
                                                    str(rng.randrange(1, 2 ** 31))])


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20180214 + i)
        n, lo, hi = SIZES[size]
        lines = list(LITERALS) if size == "S" else []
        lines += [case(rng, lo, hi) for _ in range(n)]
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n", encoding="utf-8")
