"""Seeded workload generator for Help::help (clap). Usage: python3 gen_workload.py <out_dir>

Line format (tab-separated), parsed by driver.rs:
  <kind> <flags> <help> <long_help> <spec> <next_line_help> <use_long> <force_next_line> <term_w> <longest>
kind: O (option --opt), F (flag -f), P (positional). flags: "N" (NextLineHelp on the arg) or "-".
help / long_help: "-" (none), "=<literal text>" or "#<words>:<seed>:<nl>" = <words> words
WORDS[(seed + 5*i) % len(WORDS)] joined by spaces, where every <nl>-th separator (nl > 0) is "{n}" and,
if nl < 0, every |nl|-th separator is a real newline. spec: the special-values suffix handed to the
function, same encoding. term_w: 0 = unlimited (usize::MAX). longest: the writer's `longest`.
"""
import random, sys
from pathlib import Path

LITERALS = [
    "O\t-\t=some help\t-\t-\t0\t0\t0\t120\t14",
    "O\t-\t=some help\t=long help\t-\t0\t1\t0\t120\t14",
    "O\t-\t-\t=long help only\t-\t0\t0\t0\t120\t14",
    "O\t-\t=short\t=long\t-\t0\t0\t0\t120\t14",
    "F\t-\t=prints help\t-\t-\t1\t0\t0\t120\t10",
    "F\tN\t=prints help\t-\t-\t0\t0\t0\t120\t10",
    "F\t-\t=prints help\t-\t-\t0\t0\t1\t120\t10",
    "P\t-\t=the input\t-\t= [possible values: vi, emacs]\t0\t0\t0\t120\t12",
    "O\t-\t=Some vals\t-\t= [possible values: fast, slow]\t0\t0\t0\t120\t16",
    "O\t-\t=line one{n}line two\t-\t-\t0\t0\t0\t120\t14",
    "P\t-\t=line one{n}line two{n}three\t-\t-\t0\t0\t0\t120\t14",
    "O\t-\t=has{n}break\t-\t-\t1\t0\t0\t120\t14",
    "O\t-\t#40:0:0\t-\t-\t0\t0\t0\t120\t30",
    "O\t-\t#40:3:0\t-\t= [default: x]\t0\t0\t0\t80\t20",
    "P\t-\t#40:3:0\t-\t-\t0\t0\t0\t80\t20",
    "F\t-\t#30:1:0\t-\t-\t0\t0\t1\t60\t30",
    "O\t-\t#25:2:0\t-\t-\t0\t0\t0\t20\t30",
    "O\t-\t#25:2:0\t-\t-\t0\t0\t0\t0\t30",
    "O\t-\t-\t-\t-\t0\t0\t0\t120\t14",
    "O\t-\t-\t-\t-\t1\t0\t0\t120\t14",
    "O\t-\t=\t-\t= [env: E=V]\t0\t0\t0\t120\t14",
    "O\t-\t=café 数字 ünïcödé text\t-\t-\t0\t0\t0\t30\t10",
    "O\t-\t=a real\nnewline\t-\t-\t0\t0\t0\t120\t14",
]
SIZES = {"S": (150, 0, 20), "M": (300, 50, 500), "L": (300, 1000, 10000)}


def text(rng, lo, hi):
    n = rng.randint(lo, hi)
    nl = rng.choice([0, 0, 0, 7, 25, -9, -40])
    return "#%d:%d:%d" % (n, rng.randrange(1000), nl)


def case(rng, lo, hi):
    kind = rng.choice("OOFP")
    flags = "N" if rng.random() < 0.1 else "-"
    hlp = text(rng, lo, hi) if rng.random() < 0.9 else "-"
    lhlp = text(rng, lo, hi) if rng.random() < 0.3 else "-"
    spec = rng.choice(["-", "-", "= [default: %d]" % rng.randrange(99), "#%d:%d:0" % (rng.randint(1, 8), rng.randrange(99))])
    nlh = "1" if rng.random() < 0.1 else "0"
    use_long = "1" if rng.random() < 0.15 else "0"
    force = "1" if rng.random() < 0.15 else "0"
    term_w = str(rng.choice([0, 60, 80, 100, 120, 120, 160, 300]))
    longest = str(min(rng.choice([4, 10, 14, 20, 30, 50]), (int(term_w) or 10 ** 6) - 40))  # keep >= 28 columns: textwrap 0.9 can panic on narrower multibyte input
    return "\t".join([kind, flags, hlp, lhlp, spec, nlh, use_long, force, term_w, longest])


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20180214 + i)
        n, lo, hi = SIZES[size]
        lines = [l.replace("\n", "\\n") for l in LITERALS] if size == "S" else []
        lines += [case(rng, lo, hi) for _ in range(n)]
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n", encoding="utf-8")
