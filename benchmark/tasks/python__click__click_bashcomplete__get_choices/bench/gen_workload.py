"""Seeded workload generator for get_choices. Usage: python3 gen_workload.py <out_dir>

Per-case scale grows ~10x per size: most queries carry a typed command line of ~K/2..K repeated
units (repeated options, chained subcommands, variadic values), K = 5 (S), 50 (M), 500 (L)."""
import json, random, sys
from pathlib import Path

SIZES = {"S": (5, 200), "M": (50, 200), "L": (500, 200)}   # (K, number of completion queries)

# words that make sense for each command tree in bench/clis.py
VOCAB = {
    "opts": ["--opt1", "--opt2", "--opt3", "-m", "--message", "--shout", "--no-shout", "--pos",
             "--secret", "opt11", "opt21", "opt", "m1", "m2", "pos1", "pos2", "arg11", "arg12",
             "arg21", "=", "1", "junk"],
    "chain": ["cliarg1", "cliarg2", "--cli-opt", "asub", "bsub", "csub", "dsub", "--asub-opt",
              "--bsub-opt", "--csub-opt", "arg1", "arg2", "carg1", "5"],
    "long": ["--cli-opt", "asub", "--asub-opt", "bsub", "--bsub-opt", "csub", "cother",
             "--csub-opt", "--csub", "--search-color", "foo", "bar", "baz", "red", "x"],
    "longchoice": ["sub", "--sub-opt", "subopt1", "subarg1", "subarg2", "bsub", "--bsub-opt",
                   "bsubopt1", "bsubarg1", "csub", "dsub", "esub", "fsub", "gsub", "-x"],
    "hidden": ["--name", "--choices", "1", "-v", "--verbose", "hgroup", "hgroupsub", "asub",
               "hsub", "--hname", "bob"],
    "variadic": ["subcommand", "files", "--opt", "whatever", "abc", "src1", "src2", "opt1"],
}
PRESETS = {  # likely prefixes per tree, to make realistic queries
    "opts": [[], ["--opt1"], ["--opt2"], ["--opt1", "opt11"], ["-m"], ["--pos"], ["--pos", "pos1"],
             ["--pos", "pos1", "pos2"], ["arg11"], ["--secret"]],
    "chain": [[], ["cliarg1"], ["cliarg1", "asub"], ["cliarg1", "bsub"], ["cliarg1", "asub", "csub"],
              ["cliarg1", "asub", "--asub-opt"], ["cliarg1", "bsub", "arg1", "csub"]],
    "long": [[], ["asub"], ["asub", "bsub"], ["asub", "bsub", "csub"],
             ["asub", "bsub", "csub", "--csub-opt"], ["asub", "bsub", "csub", "--search-color"],
             ["asub", "bsub", "cother"], ["asub", "bsub", "cother", "x"]],
    "longchoice": [[], ["sub"], ["sub", "--sub-opt"], ["sub", "subarg1"], ["sub", "subarg1", "bsub"],
                   ["sub", "subarg1", "bsub", "--bsub-opt"], ["sub", "subarg1", "csub"],
                   ["sub", "esub"], ["sub", "esub", "fsub"], ["sub", "esub", "fsub", "-x"]],
    "hidden": [[], ["--choices"], ["hgroup"], ["hsub"], ["-v"], ["asub"]],
    "variadic": [[], ["subcommand"], ["subcommand", "--opt"], ["subcommand", "whatever", "--opt"],
                 ["files"], ["files", "src1"], ["files", "src1", "--opt"]],
}
TREES = list(VOCAB)


def scaled_args(rng, tree, K):
    n = rng.randint(max(1, K // 2), K)
    pick = lambda units: [w for _ in range(n) for w in rng.choice(units)]
    if tree == "opts":
        return pick([["-m", "m1"], ["--message", "m2"], ["--opt1", "opt11"], ["--shout"], ["--pos", "pos1", "pos2"]])
    if tree == "chain":
        return ["cliarg1"] + pick([["asub"], ["bsub", "arg1"], ["csub"], ["asub", "--asub-opt", "5"], ["csub", "carg2"]])
    if tree == "long":
        if rng.random() < 0.5:
            return pick([["--cli-opt", "v"]]) + ["asub", "bsub", rng.choice(["csub", "cother"])]
        return ["asub", "bsub", "cother"] + pick([["x"], ["foo"], ["abc"]])
    if tree == "longchoice":
        return ["sub", "esub"] + pick([["fsub"], ["gsub"], ["fsub", "-x"]])
    if tree == "hidden":
        return pick([["-v"], ["--verbose"]]) + rng.choice([[], ["asub"], ["hgroup"]])
    if rng.random() < 0.5:
        return ["files"] + pick([["src1"], ["src2"], ["--opt", "opt1"]])
    return ["subcommand"] + pick([["whatever"], ["abc"], ["--opt", "x"]])


def query(rng, K):
    tree = rng.choice(TREES)
    vocab = VOCAB[tree]
    args = list(rng.choice(PRESETS[tree])) if rng.random() < 0.25 else scaled_args(rng, tree, K)
    for _ in range(rng.choice([0, 0, 0, 1, 1, 2, 3])):
        args.append(rng.choice(vocab))
    r = rng.random()
    if r < 0.2:
        inc = ""
    elif r < 0.35:
        inc = rng.choice(["-", "--", "="])
    elif r < 0.85:
        w = rng.choice(vocab)
        inc = w[:rng.randint(0, len(w))]
    else:
        w = rng.choice([v for v in vocab if v.startswith("--")])
        val = rng.choice(vocab)
        inc = w + "=" + val[:rng.randint(0, len(val))]
    return {"tree": tree, "args": args, "incomplete": inc}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (K, n)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([query(rng, K) for _ in range(n)]))
