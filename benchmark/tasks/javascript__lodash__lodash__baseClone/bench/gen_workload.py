"""Seeded workload generator for lodash baseClone (via _.clone / _.cloneDeep / _.cloneWith / _.cloneDeepWith). Usage: python3 gen_workload.py <out_dir>

Each case: {"seed": s, "n": approx node count, "fn": clone|cloneDeep|cloneWith|cloneDeepWith, "shape": tree|wide|list|graph}
The driver builds the source value from `seed` before timing: a structure of ~n nodes mixing plain objects,
arrays (sparse, with expandos), class instances, Maps, Sets, Dates, RegExps, boxed primitives, typed arrays,
symbol keys, functions and errors (uncloneable), with shared and circular references ("graph").
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190710
SIZES = {"S": (16, 1_000), "M": (16, 10_000), "L": (16, 100_000)}
FNS = ["cloneDeep", "cloneDeep", "cloneDeep", "clone", "cloneDeepWith", "cloneWith"]
SHAPES = ["tree", "wide", "list", "graph"]


def cases(cnt, n, rng, small):
    out = []
    if small:
        for f in ["clone", "cloneDeep", "cloneWith", "cloneDeepWith"]:
            for s in SHAPES:
                out.append({"seed": rng.randint(0, 2**31 - 1), "n": rng.choice([1, 5, 20]), "fn": f, "shape": s})
    for _ in range(cnt):
        out.append({"seed": rng.randint(0, 2**31 - 1), "n": rng.randint(n // 2, n),
                    "fn": rng.choice(FNS), "shape": rng.choice(SHAPES)})
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (cnt, n)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(cnt, n, rng, size == "S")))
