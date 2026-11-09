"""Seeded workload generator for completions::fish::gen_fish_inner (clap). Usage: python3 gen_workload.py <out_dir>

One command tree per line (tab-separated), expanded deterministically by driver.rs:
  <root> <parent_cmds> <n_opts> <n_flags> <n_subcmds> <depth> <seed>
root: the `-c` command name; parent_cmds: the initial command path ("-" = empty string).
Every (sub)command at depth < <depth> gets <n_subcmds> subcommands; every command gets about <n_opts> options and
<n_flags> flags (the driver's xorshift PRNG, seeded with <seed>, varies counts, short/long presence, help texts with
quotes and backslashes, possible values and subcommand abouts).
"""
import random, sys
from pathlib import Path

LITERALS = [
    "myapp\tmyapp\t1\t2\t2\t1\t1", "myapp\tmyapp\t0\t0\t0\t0\t2", "myapp\t-\t2\t2\t1\t2\t3", "my-app\tmy-app\t3\t0\t0\t0\t4",
    "x\tx\t0\t3\t3\t1\t5", "prog\tprog sub\t2\t2\t2\t2\t6", "café\tcafé\t1\t1\t1\t1\t7", "q\tq\t4\t4\t0\t0\t8",
]
SIZES = {"S": (24, 1, 4, 1), "M": (24, 10, 40, 2), "L": (24, 150, 600, 3)}  # (cases, lo, hi, max_depth)


def case(rng, lo, hi, md):
    depth = rng.randint(0, md)
    n_sub = rng.randint(1, 4) if depth else 0
    root = rng.choice(["myapp", "prog", "tool-x"])
    return "\t".join(str(x) for x in [root, root, rng.randint(lo, hi), rng.randint(lo, hi), n_sub, depth,
                                      rng.randrange(1, 2 ** 31)])


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20180214 + i)
        n, lo, hi, md = SIZES[size]
        lines = list(LITERALS) if size == "S" else []
        lines += [case(rng, lo, hi, md) for _ in range(n)]
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n", encoding="utf-8")
