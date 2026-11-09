"""Seeded workload generator for lodash arrayLikeKeys (via _.keys / _.keysIn). Usage: python3 gen_workload.py <out_dir>

Each case: {"kind": k, "n": length, "holes": h, "extra": [keys], "proto": [keys], "inherited": bool}
kind: arr | args | typed | buffer | strobj | str | arraylike. The driver builds the value before timing:
holes>0 deletes every h-th element (arr/args only); "extra" are added as own enumerable props;
"proto" (arr/strobj/arraylike only) are enumerable props of a custom prototype inserted below the
value's normal prototype.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190710
SIZES = {"S": (120, 100), "M": (120, 1_000), "L": (120, 10_000)}
KINDS = ["arr", "arr", "args", "typed", "buffer", "strobj", "str", "arraylike"]


def extra_keys(rng, n):
    pool = ["a", "b", "length", "offset", "parent", "buffer", "byteLength", "byteOffset",
            "-1", "1.5", "01", "x" + str(rng.randint(0, 99)), str(n + rng.randint(0, 5)),
            str(max(n - 1, 0)), "constructor", "__key"]
    return rng.sample(pool, rng.randint(0, 6))


FIXED = [
    {"kind": "arr", "n": 0, "holes": 0, "extra": [], "proto": [], "inherited": False},
    {"kind": "arr", "n": 3, "holes": 2, "extra": [], "proto": [], "inherited": False},
    {"kind": "arr", "n": 1, "holes": 0, "extra": ["a"], "proto": ["a"], "inherited": True},
    {"kind": "arr", "n": 1, "holes": 0, "extra": [], "proto": ["a"], "inherited": False},
    {"kind": "args", "n": 3, "holes": 0, "extra": ["a", "7", "length"], "proto": [], "inherited": False},
    {"kind": "args", "n": 3, "holes": 0, "extra": [], "proto": [], "inherited": True},
    {"kind": "strobj", "n": 3, "holes": 0, "extra": [], "proto": [], "inherited": False},
    {"kind": "strobj", "n": 1, "holes": 0, "extra": ["a"], "proto": ["b"], "inherited": True},
    {"kind": "str", "n": 3, "holes": 0, "extra": [], "proto": [], "inherited": False},
    {"kind": "str", "n": 0, "holes": 0, "extra": [], "proto": [], "inherited": True},
    {"kind": "arraylike", "n": 1, "holes": 0, "extra": [], "proto": [], "inherited": False},
    {"kind": "typed", "n": 2, "holes": 0, "extra": ["buffer", "q"], "proto": [], "inherited": False},
    {"kind": "buffer", "n": 2, "holes": 0, "extra": ["offset", "parent", "z"], "proto": [], "inherited": False},
]


def cases(cnt, max_n, rng, with_fixed):
    out = list(FIXED) if with_fixed else []
    for _ in range(cnt):
        kind = rng.choice(KINDS)
        n = rng.randint(max_n // 2, max_n)
        out.append({
            "kind": kind, "n": n,
            "holes": rng.choice([0, 0, 3, 7]) if kind in ("arr", "args") else 0,
            "extra": extra_keys(rng, n),
            "proto": rng.sample(["p", "q", "length", "1", str(n + 2)], rng.randint(0, 2))
            if kind in ("arr", "strobj", "arraylike") else [],
            "inherited": rng.random() < 0.5,
        })
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (cnt, m)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(cnt, m, rng, size == "S")))
