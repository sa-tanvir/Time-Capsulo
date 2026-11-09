"""Seeded workload generator for lodash isEmpty. Usage: python3 gen_workload.py <out_dir>

Each case is {"kind": k, "n": size, "own": m}; the driver builds the value before timing:
  prim      : one of a fixed list of primitives (n selects it)
  arr/str/args/typed/buffer/splice : collection of length n
  map/set   : Map/Set with n entries
  obj       : plain object with n own keys
  inherit   : instance whose prototype chain holds n enumerable keys, plus m own keys (m mostly 0)
  proto     : a constructor's prototype object holding `constructor` plus n keys
  lenobj    : object with own `length` = n (or bad lengths via prototype when m = 1)
  func      : function with n own enumerable props
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190710
SIZES = {"S": (400, 100), "M": (400, 1_000), "L": (400, 10_000)}
KINDS = ["prim", "arr", "str", "args", "typed", "buffer", "splice", "map", "set", "obj",
         "inherit", "inherit", "inherit", "proto", "proto", "lenobj", "func"]

FIXED = [{"kind": "prim", "n": i, "own": 0} for i in range(10)] + [
    {"kind": k, "n": n, "own": 0}
    for k in ["arr", "str", "args", "typed", "buffer", "splice", "map", "set", "obj", "inherit", "proto", "func"]
    for n in (0, 1)
] + [{"kind": "lenobj", "n": 0, "own": 0}, {"kind": "lenobj", "n": -1, "own": 1},
     {"kind": "lenobj", "n": 9007199254740992, "own": 1}, {"kind": "lenobj", "n": "0", "own": 0},
     {"kind": "inherit", "n": 5, "own": 1}]


def cases(cnt, max_n, rng, with_fixed):
    out = list(FIXED) if with_fixed else []
    for _ in range(cnt):
        kind = rng.choice(KINDS)
        n = rng.choice([0, rng.randint(max_n // 2, max_n)]) if kind not in ("prim", "inherit", "proto") \
            else (rng.randint(0, 9) if kind == "prim" else rng.randint(max_n // 2, max_n))
        own = 1 if (kind == "inherit" and rng.random() < 0.2) or (kind == "proto" and rng.random() < 0.3) else 0
        out.append({"kind": kind, "n": n, "own": own})
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (cnt, m)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(cnt, m, rng, size == "S")))
