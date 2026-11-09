"""Seeded workload generator for SortedList._pos. Usage: python3 gen_workload.py <out_dir>"""
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

SIZES = {"S": (12, 1_000, 2_000), "M": (12, 10_000, 2_000), "L": (12, 100_000, 2_000)}  # (cases, max n, queries)


def make(rng, n_cases, max_n, n_q):
    out = []
    for i in range(n_cases):
        c = container(rng, max_n, i % 3 == 2)    # every third container is a SortedKeyList
        n = c["n"]
        c["queries"] = [rng.randint(-n - 3, n + 2) if rng.random() < 0.1 else
                        (rng.randint(0, n - 1) if rng.random() < 0.7 else rng.randint(-n, -1)) if n else
                        rng.randint(-3, 3) for _ in range(n_q)]
        out.append(c)
    return out


if __name__ == "__main__":
    write(sys.argv[1], SIZES, make)
