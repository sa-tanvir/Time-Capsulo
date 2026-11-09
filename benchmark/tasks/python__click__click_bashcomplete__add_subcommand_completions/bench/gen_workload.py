"""Seeded workload generator for add_subcommand_completions. Usage: python3 gen_workload.py <out_dir>

Per-case scale grows ~10x per size: the groups of the large command tree each hold about
10 (S), 100 (M) or 1000 (L) subcommands, and chained command lines name up to 5/50/500 of them."""
import json, random, sys
from pathlib import Path

SIZES = {"S": (10, 300), "M": (100, 300), "L": (1000, 300)}   # (subcommands per group, queries)
SYLL = ['ba', 'ce', 'di', 'fo', 'gu', 'ka', 'le', 'mi', 'no', 'pu']


def big_names(n):
    """Names of the first n subcommands of a group in bench/clis.py:build_big (offset-independent set)."""
    return [SYLL[k % 10] + SYLL[(k // 10) % 10] + str(k // 100) for k in range(n)]

PRESETS = {
    "chain": [[], ["cliarg1"], ["cliarg1", "asub"], ["cliarg1", "bsub"], ["cliarg1", "asub", "csub"],
              ["cliarg1", "asub", "--asub-opt", "5", "bsub"], ["cliarg1", "bsub", "arg1", "csub"],
              ["cliarg1", "dsub"]],
    "long": [[], ["asub"], ["asub", "bsub"], ["asub", "bsub", "csub"], ["asub", "bsub", "cother"]],
    "longchoice": [[], ["sub"], ["sub", "subarg1"], ["sub", "subarg1", "bsub"], ["sub", "csub"],
                   ["sub", "esub"], ["sub", "esub", "fsub"], ["sub", "esub", "fsub", "-x", "gsub"]],
    "hidden": [[], ["hgroup"], ["hsub"], ["asub"], ["-v"]],
    "variadic": [[], ["subcommand"], ["files", "src1"]],
    "opts": [[], ["--opt1", "opt11"]],
}
PREFIXES = ["", "", "a", "b", "c", "d", "e", "f", "g", "h", "s", "su", "cs", "x"]


def query(rng, n):
    if rng.random() < 0.7:
        start = rng.choice([["pipe"], ["nested", "inner"], [], ["nested"]])
        args = list(start)
        if start and start[-1] in ("pipe", "inner"):
            names = big_names(n)
            args += [rng.choice(names) for _ in range(rng.randint(0, max(1, n // 2)))]
        names = big_names(n)
        inc = rng.choice(["", "", rng.choice(SYLL), rng.choice(SYLL)[:1], rng.choice(names)[:3],
                          rng.choice(names)[:4]])
        return {"tree": "big", "args": args, "incomplete": inc}
    tree = rng.choice(list(PRESETS))
    return {"tree": tree, "args": rng.choice(PRESETS[tree]), "incomplete": rng.choice(PREFIXES)}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, q)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        data = {"passes": 1, "big_n": n, "queries": [query(rng, n) for _ in range(q)]}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(data))
