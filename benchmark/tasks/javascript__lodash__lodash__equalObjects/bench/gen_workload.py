"""Seeded workload generator for lodash equalObjects (via _.isEqual / _.isEqualWith / _.isMatch). Usage: python3 gen_workload.py <out_dir>

Each case: {"seed": s, "kind": k, "n": keys, "variant": v}. The driver builds the two compared objects from
`seed` before timing. kind: wide | nested | instances | symbols | nullproto | args | match | custom | cyclic.
variant: same (equal, keys inserted in another order) | diff (one value changed) | extra (one more key) |
ctor (different constructor / prototype, where meaningful).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190710
SIZES = {"S": (60, 1_000), "M": (60, 10_000), "L": (60, 100_000)}
KINDS = ["wide", "wide", "nested", "instances", "symbols", "nullproto", "args", "match", "custom", "cyclic"]
VARIANTS = ["same", "same", "diff", "extra", "ctor"]


def cases(cnt, max_n, rng, with_small):
    out = []
    if with_small:
        for k in KINDS:
            for v in ("same", "diff", "extra", "ctor"):
                out.append({"seed": rng.randint(0, 2**31 - 1), "kind": k, "n": rng.choice([0, 1, 3]), "variant": v})
    for _ in range(cnt):
        out.append({"seed": rng.randint(0, 2**31 - 1), "kind": rng.choice(KINDS),
                    "n": rng.randint(max_n // 2, max_n), "variant": rng.choice(VARIANTS)})
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (cnt, m)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(cnt, m, rng, size == "S")))
