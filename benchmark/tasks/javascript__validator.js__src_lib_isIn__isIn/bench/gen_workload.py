"""Seeded workload generator for isIn(str, options). Usage: python3 gen_workload.py <out_dir>

Each case is [str] or [str, options]; options is an array, a plain object, a string or another value.
Array elements may be {"$tostr": s} (object whose toString() returns s), {"$obj": {...}} (plain object)
or {"$notostr": 1} (object without a callable toString); the driver builds them.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20191121
# (cases, collection size range): ~10 / ~100 / ~1000 elements, keys or 10x characters
SIZES = {"S": (300, (0, 20)), "M": (300, (50, 150)), "L": (300, (500, 1500))}

WORDS = ["foo", "bar", "baz", "qux", "1", "2", "3", "10", "true", "null", "", "[object Object]", "Foo", "f", "oo"]


def word(rng):
    if rng.random() < 0.5:
        return rng.choice(WORDS)
    return "".join(rng.choice("abcdef0123") for _ in range(rng.randint(1, 6)))


def elem(rng):
    r = rng.random()
    if r < 0.6:
        return word(rng)
    if r < 0.75:
        return rng.choice([rng.randint(-5, 50), 1.5, 0, True, False])
    if r < 0.82:
        return None
    if r < 0.9:
        return {"$tostr": word(rng)}
    if r < 0.96:
        return {"$obj": {"foo": "bar"}}
    return {"$notostr": 1}


def case(rng, lens):
    n = rng.randint(*lens)
    kind = rng.random()
    if kind < 0.5:
        opts = [elem(rng) for _ in range(n)]
        pool = [e for e in opts if isinstance(e, str)]
    elif kind < 0.75:
        keys = sorted({word(rng) for _ in range(n)})
        opts = {k: rng.randint(0, 3) for k in keys if not k.startswith("$")}
        pool = list(opts)
    elif kind < 0.95:
        opts = "".join(word(rng) for _ in range(n * 2))
        pool = [opts[i:i + rng.randint(0, 8)] for i in range(0, max(1, len(opts)), max(1, len(opts) // 5 + 1))]
    else:
        opts = rng.choice([None, 0, 7, False, True])
        pool = []
        if opts is None:
            return [word(rng)]
    s = rng.choice(pool) if pool and rng.random() < 0.5 else word(rng)
    return [s, opts]


FIXED = [
    ("foobar", ["foo", "bar", "foobar", "", "foobarbaz", "barfoo"]),
    (["foo", "bar"], ["foo", "bar", "foobar", "barfoo", ""]),
    (["1", "2", "3"], ["1", "2", "3", "4", ""]),
    (["1", "2", "3", {"$obj": {"foo": "bar"}}, {"$notostr": 1}, None, 5, True, {"$tostr": "x"}],
     ["1", "2", "3", "", "4", "[object Object]", "5", "true", "x", "null"]),
    ({"foo": 1, "bar": 2, "foobar": 3}, ["foo", "bar", "foobar", "foobarbaz", "barfoo", "", "toString", "hasOwnProperty"]),
    ({"1": 3, "2": 0, "3": 1}, ["1", "2", "3", "4", ""]),
    ([], ["", "a"]),
    ({}, ["", "a"]),
    ("", ["", "a"]),
]


def cases(n, lens, rng, with_fixed):
    out = []
    if with_fixed:
        for opts, strs in FIXED:
            out += [[s, opts] for s in strs]
        out += [["foo"], [""], ["foo", 5], ["foo", True], ["1", 1], ["foo", None], [None, ["a"]], [3, "345"]]
    out += [case(rng, lens) for _ in range(n)]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lens)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, lens, rng, size == "S")))
