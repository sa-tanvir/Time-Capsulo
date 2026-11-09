"""Seeded workload generator for SortedList.__delitem__. Usage: python3 gen_workload.py <out_dir>"""
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

SIZES = {"S": (12, 1_000), "M": (12, 10_000), "L": (12, 100_000)}  # (cases, max n); ops ~ n/10 + 30


def opt(rng, v):
    return None if rng.random() < 0.15 else v


def op(rng, n):
    """One deletion against a list of current length n (the generator tracks n exactly)."""
    r = rng.random()
    if r < 0.85 or n == 0:
        if rng.random() < 0.04 or n == 0:
            return rng.choice([n, n + 3, -n - 1]), 0          # IndexError, no change
        i = rng.randint(0, n - 1) if rng.random() < 0.7 else rng.randint(-n, -1)
        return i, 1
    if r < 0.97:                                               # short slice, any step
        a = rng.randint(-n - 2, n + 2)
        s = slice(opt(rng, a), opt(rng, a + rng.randint(-5, 60)), rng.choice([None, 1, 1, -1, 2, -3]))
    elif r < 0.995:                                            # long slice (bulk deletion)
        a, b = sorted([rng.randint(0, n), rng.randint(0, n)])
        s = slice(a, b, rng.choice([None, 1, 1, 2, -1]))
    else:
        return {"s": [None, None, 0]}, 0                       # ValueError, no change
    return {"s": [s.start, s.stop, s.step]}, len(range(*s.indices(n)))


def make(rng, n_cases, max_n):
    out = []
    for i in range(n_cases):
        c = container(rng, max_n, i % 3 == 2)    # every third container is a SortedKeyList
        n, ops = c["n"], []
        for _ in range(c["n"] // 10 + 30):
            o, removed = op(rng, n)
            ops.append(o)
            n -= removed
        c["ops"] = ops
        out.append(c)
    return out


if __name__ == "__main__":
    write(sys.argv[1], SIZES, make)
