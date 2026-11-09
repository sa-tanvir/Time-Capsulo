"""Seeded workload generator for Help::val (clap). Usage: python3 gen_workload.py <out_dir>

Line format (tab-separated), parsed by driver.rs; "-" means "not set":
  <kind> <long> <short> <flags> <delim> <num_vals> <val_names> <help_words> <n_possible> <next_line_help> <term_w> <extra>
kind: O (option), F (flag), P (positional). flags: subset of M (Multiple), D (RequireDelimiter), E (RequireEquals),
N (NextLineHelp on the argument), or "-". val_names: space-separated names, or "#<count>:<seed>" = <count> names
WORDS[(seed + 7*i) % len(WORDS)]. help_words: help text = that many words WORDS[(i*3) % len] joined by spaces
("-" = no help). n_possible: number of possible values (WORDS[i % len]). next_line_help: writer-wide flag 0/1.
term_w: writer width. extra: the writer's `longest` is set to display_width(arg signature) + extra.
"""
import random, sys
from pathlib import Path

LITERALS = [
    "O\toption\to\t-\t-\t-\t-\t3\t0\t0\t120\t0",
    "O\toption\to\tM\t-\t-\t-\t3\t0\t0\t120\t5",
    "O\t-\to\t-\t-\t-\tfile name\t3\t0\t0\t120\t2",
    "O\tfake\tf\tD\t:\t2\tsome val\t2\t0\t0\t120\t0",
    "O\topt\to\tE\t-\t-\tFILE\t2\t0\t0\t120\t0",
    "O\topt\t-\tM\t-\t1\t-\t2\t2\t0\t120\t0",
    "O\topt\t-\tDM\t,\t3\t-\t2\t0\t0\t120\t1",
    "O\t-\to\tM\t-\t-\tval\t1\t0\t0\t120\t3",
    "F\tflag\tf\t-\t-\t-\t-\t3\t0\t0\t120\t4",
    "F\t-\tf\t-\t-\t-\t-\t3\t0\t0\t120\t4",
    "F\tflag\t-\tN\t-\t-\t-\t3\t0\t0\t120\t4",
    "P\t-\t-\t-\t-\t-\t-\t3\t0\t0\t120\t0",
    "P\t-\t-\tM\t-\t-\t-\t3\t2\t0\t120\t6",
    "P\t-\t-\t-\t-\t-\tA B\t3\t0\t0\t120\t0",
    "P\t-\t-\tM\t-\t2\t-\t3\t0\t0\t120\t0",
    "P\t-\t-\t-\t-\t-\t-\t3\t0\t1\t120\t0",
    "O\toption\to\t-\t-\t-\t-\t40\t0\t0\t120\t30",
    "O\toption\to\t-\t-\t-\t-\t40\t0\t0\t120\t2",
    "O\toption\to\t-\t-\t-\t-\t12\t5\t0\t60\t25",
    "F\tflag\tf\t-\t-\t-\t-\t30\t0\t0\t40\t30",
    "O\toption\to\t-\t-\t-\t-\t10\t0\t0\t0\t10",
    "O\toption\to\tN\t-\t-\t-\t10\t0\t0\t80\t10",
    "P\t-\t-\t-\t-\t-\t-\t50\t0\t0\t100\t40",
    "O\t-\tö\tM\t-\t-\t数\t1\t0\t0\t120\t0",
]
SIZES = {"S": (150, 0, 5), "M": (300, 30, 300), "L": (400, 600, 6000)}


def case(rng, lo, hi):
    kind = rng.choice("OOOFP")
    long_, short = "-", "-"
    if kind != "P":
        long_ = rng.choice(["-", "opt%d" % rng.randrange(99), "long-name-%d" % rng.randrange(9)])
        short = rng.choice("abcxyzö") if long_ == "-" or rng.random() < 0.6 else "-"
    flags = "".join(f for f in "MDEN" if rng.random() < (0.1 if f == "N" else 0.3)) or "-"
    delim = rng.choice(",:;") if "D" in flags else "-"
    n = rng.randint(lo, hi)
    num_vals, names = "-", "-"
    k = rng.randrange(3)
    if kind != "F" and k == 0:
        num_vals = str(max(n, 1))
    elif kind != "F" and k == 1 and n > 0:
        names = "#%d:%d" % (n, rng.randrange(1000))
    help_words = str(rng.randint(0, max(4, hi // 10))) if rng.random() < 0.9 else "-"
    npv = rng.choice([0, 0, rng.randint(0, max(3, hi // 20))])
    nlh = "1" if rng.random() < 0.1 else "0"
    term_w = str(rng.choice([0, 40, 80, 120, 120, 200, 10 ** 6]))
    extra = str(rng.choice([0, 1, 4, 10, 30, 60]))
    return "\t".join([kind, long_, short, flags, delim, num_vals, names, help_words, str(npv), nlh, term_w, extra])


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20180214 + i)
        n, lo, hi = SIZES[size]
        lines = list(LITERALS) if size == "S" else []
        lines += [case(rng, lo, hi) for _ in range(n)]
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n", encoding="utf-8")
