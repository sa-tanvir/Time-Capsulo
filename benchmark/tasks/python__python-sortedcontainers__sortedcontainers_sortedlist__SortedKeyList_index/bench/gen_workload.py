"""Seeded workload generator for SortedKeyList_index. Usage: python3 gen_workload.py <out_dir>"""
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
SIZES = {"S": (12, 1_000, 400), "M": (12, 10_000, 400), "L": (12, 100_000, 400)}  # (cases, max n, queries)


def bound(rng, n):
    return rng.choice([None, None, rng.randint(0, n), rng.randint(-n, -1) if n else -1,
                       rng.randint(-3 * n - 5, 3 * n + 5)])


def make(rng, n_cases, max_n, n_q):
    out = []
    for _ in range(n_cases):
        c = container(rng, max_n, KEYED)
        n, vmax = c["n"], c["vmax"]
        c["queries"] = [[rng.randint(-2, vmax + 2), bound(rng, n), bound(rng, n)] for _ in range(n_q)]
        out.append(c)
    return out


if __name__ == "__main__":
    write(sys.argv[1], SIZES, make)
