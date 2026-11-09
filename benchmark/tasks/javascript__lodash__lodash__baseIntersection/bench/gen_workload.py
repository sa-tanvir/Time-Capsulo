"""Seeded workload generator for lodash baseIntersection (via the public _.intersection / _.intersectionBy / _.intersectionWith wrappers). Usage: python3 gen_workload.py <out_dir>

Each case: {"seed": s, "kind": "num"|"str"|"obj"|"mixed"|"float", "mode": "plain"|"by"|"with",
            "lens": [n0, n1, ...] (array lengths), "dom": domain size}
The driver generates every array element deterministically from `seed` (LCG) before timing:
values are drawn from a domain of `dom` distinct keys (numbers incl. -0/NaN, strings, shared objects,
mixed primitives/symbols, or floats whose Math.floor is the key).
"mode" selects plain equality, an iteratee (floor for numbers, identity otherwise / 'id' property), or a comparator (_.eq / id-equality).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190710
OP = "intersection"
SIZES = {"S": (40, 1_000), "M": (40, 10_000), "L": (40, 100_000)}


def case(rng, n):
    kind = rng.choice(["num", "num", "str", "obj", "mixed", "float"])
    mode = rng.choice(["plain", "plain", "plain", "by", "by", "with"])
    if kind == "float":
        mode = "by" if mode != "with" else "plain"
    if kind == "obj" and mode == "by":
        pass
    scale = 1 if mode != "with" else 40   # comparator mode is quadratic: keep it small
    big = max(rng.randint(n // 2, n) // scale, 4)
    if OP == "uniq":
        lens = [big]
        dom = rng.choice([big // 50 + 1, big // 4 + 1, big * 2])
    elif OP == "difference":
        lens = [big, rng.choice([3, 50, 199, 200, big // 3 + 1, big])]
        dom = rng.choice([big // 2 + 1, big, big * 3])
    else:
        k = rng.choice([2, 2, 3, 4])
        lens = [big] + [rng.choice([big, big // 2 + 1, 150, 30]) for _ in range(k - 1)]
        dom = rng.choice([big // 2 + 1, big, big * 2])
    return {"seed": rng.randint(0, 2**31 - 1), "kind": kind, "mode": mode, "lens": lens, "dom": dom}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (cnt, n)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cs = [case(rng, n) for _ in range(cnt)]
        if size == "S":  # tiny cases
            cs += [{"seed": s, "kind": k, "mode": m, "lens": [l] * (2 if OP != "uniq" else 1), "dom": 3}
                   for s, k, m, l in [(1, "num", "plain", 0), (2, "num", "plain", 1), (3, "mixed", "plain", 8),
                                      (4, "num", "with", 6), (5, "obj", "by", 5), (6, "float", "by", 4)]]
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cs))
