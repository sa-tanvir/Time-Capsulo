"""Seeded workload generator for MultiCommand.invoke. Usage: python3 gen_workload.py <out_dir>

Each case names one of the driver's groups and the command line after the group name.
Per-case scale grows ~10x per size: chained command lines hold ~10 (S), 100 (M), 1000 (L)
subcommand invocations; single-subcommand lines pass that many positional values."""
import json, random, sys
from pathlib import Path

SIZES = {"S": (10, 40), "M": (100, 40), "L": (1000, 40)}   # (scale, cases)


def chain_tokens(rng, n):
    out = []
    for _ in range(n):
        k = rng.choice(["a", "a", "b", "c"])
        out.append(k)
        if k == "b" and rng.random() < 0.7:
            if rng.random() < 0.5:
                out.append("--format=%d" % rng.randint(0, 9))
            else:
                out += ["--format", rng.choice(["tar", "zip"])]
        elif k == "c":
            out.append("v%d" % rng.randint(0, 999))
    return out


def case(rng, scale):
    r = rng.random()
    if r < 0.45:
        g = rng.choice(["chain", "chain_rc", "chain_iwc"])
        toks = (["--debug"] if rng.random() < 0.3 else []) + chain_tokens(rng, rng.randint(max(1, scale // 2), scale))
        if rng.random() < 0.1:
            toks.insert(rng.randrange(len(toks) + 1), "nosuch")
        return [g, toks]
    if r < 0.75:
        g = rng.choice(["single", "single_rc", "single_iwc"])
        head = ["--debug"] if rng.random() < 0.3 else []
        if rng.random() < 0.15:
            return [g, head + [rng.choice(["sync", "nosuch"])]]
        vals = [str(rng.randint(0, 10**6)) for _ in range(rng.randint(max(1, scale // 2), scale))]
        return [g, head + ["collect"] + vals]
    if r < 0.9:
        return [rng.choice(["single_iwc", "chain_iwc"]), rng.choice([[], ["--debug"]])]
    return [rng.choice(["withobj", "single"]), rng.choice([["obj1"], ["--debug"], []]) if rng.random() < 0.5
            else ["obj1", "sync"]]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (scale, n)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        data = {"cases": [case(rng, scale) for _ in range(n)]}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(data))
