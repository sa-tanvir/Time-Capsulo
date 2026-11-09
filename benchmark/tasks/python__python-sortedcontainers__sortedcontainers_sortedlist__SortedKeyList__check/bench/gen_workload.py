"""Seeded workload generator for SortedKeyList._check. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path


def container(rng, max_n, keyed, dup=None):
    """Recipe for a sorted (key) list; the driver expands it deterministically."""
    n = rng.choice([0, 1, 2, 7]) if rng.random() < 0.08 else rng.randint(max_n // 3, max_n)
    dup = dup if dup is not None else rng.choice([0.3, 1, 1, 4])   # values per distinct value
    return {
        "seed": rng.randint(0, 2**31),
        "n": n,
        "vmax": max(1, int(n / dup)),
        "load": rng.choice([4, 17, 64, 300, 1000]),
        "key": rng.choice(["neg", "div3", "mod101"]) if keyed else None,
        "prebuild": rng.random() < 0.5,
    }


def write(out_dir, sizes, make):
    for i, (size, args) in enumerate(sizes.items()):
        rng = random.Random(20181122 + i)
        (Path(out_dir) / f"workload_{size}.json").write_text(json.dumps(make(rng, *args)))

KEYED = True
SIZES = {"S": (24, 1_000), "M": (16, 10_000), "L": (12, 100_000)}  # (valid cases, max n)
CORRUPT = ["len", "load", "maxes", "maxes_len", "swap", "shrink_load", "index_root", "index_leaf",
           "index_inner"] + (["key"] if KEYED else [])


def make(rng, n_cases, max_n):
    out = []
    for _ in range(n_cases):
        c = container(rng, max_n, KEYED)
        c["corrupt"] = None
        out.append(c)
    for kind in CORRUPT:                      # small corrupted containers (the dump is printed)
        for _ in range(2):
            c = container(rng, 300, KEYED)
            c["n"] = max(c["n"], 40)
            c["vmax"] = max(c["vmax"], 20)
            c["load"] = rng.choice([4, 8, 17])
            c["prebuild"] = kind.startswith("index") or c["prebuild"]
            c["corrupt"] = kind
            c["where"] = rng.random()
            out.append(c)
    return out


if __name__ == "__main__":
    write(sys.argv[1], SIZES, make)
