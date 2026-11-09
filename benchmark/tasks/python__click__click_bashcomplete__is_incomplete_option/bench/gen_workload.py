"""Seeded workload generator for is_incomplete_option. Usage: python3 gen_workload.py <out_dir>

Per-case scale grows ~10x per size: the argument list of each query holds up to 10 (S),
100 (M) or 1000 (L) words."""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (10, 300), "M": (100, 300), "L": (1000, 300)}   # (max args per query, queries)


def params(rng):
    out = []
    for k in range(24):
        name = "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(2, 6))) + str(k)
        kind = rng.choice(["opt", "opt", "opt", "flag", "boolpair", "count", "arg"])
        p = {"kind": kind, "nargs": 1}
        if kind == "arg":
            p["decls"] = [name]
            p["nargs"] = rng.choice([1, 2, -1])
        elif kind == "boolpair":
            p["decls"] = ["--%s/--no-%s" % (name, name)]
        else:
            p["decls"] = ["--" + name] + (["-" + chr(65 + k)] if rng.random() < 0.6 else [])
            if kind == "opt":
                p["nargs"] = rng.choice([1, 1, 1, 2, 3])
        out.append(p)
    return out


def query(rng, ps, max_args):
    words = [d for p in ps if p["kind"] != "arg" for d in p["decls"]]
    words = [w2 for w in words for w2 in (w.split("/") if w.count("/") == 1 else [w])]
    words += ["=", "=", "value", "1", "x y", "-", "--", "--unknown", "-q"]
    pi = rng.randrange(len(ps))
    n = rng.choice([0, 1, 2, rng.randint(0, max_args), max_args, max_args])
    args = [rng.choice(words) for _ in range(n)]
    if args and rng.random() < 0.5 and ps[pi]["kind"] != "arg":
        cut = rng.randint(0, len(args) - 1)
        args = args[:cut] + [rng.choice(ps[pi]["decls"])] + args[cut + 1:cut + 1 + rng.randint(0, 3)]
    return [pi, args]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (max_args, n)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        ps = params(rng)
        data = {"params": ps, "passes": 1, "queries": [query(rng, ps, max_args) for _ in range(n)]}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(data))
