"""Seeded workload generator for lodash baseSortedIndexBy (via _.sortedIndexBy & co). Usage: python3 gen_workload.py <out_dir>

Each case describes one sorted array the driver builds before timing, plus queries:
  {"seed": s, "kind": "num"|"str"|"obj"|"mixed", "n": ordinary elements, "special": k (count of each special
   class appended: symbols, null, undefined, NaN; mixed only), "q": number of queries}
The driver derives the array and the query values deterministically from `seed`.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190710
SIZES = {"S": (60, 1_000), "M": (60, 10_000), "L": (60, 100_000)}


def cases(cnt, max_n, rng):
    out = []
    for _ in range(cnt):
        kind = rng.choice(["num", "str", "obj", "mixed", "mixed"])
        out.append({"seed": rng.randint(0, 2**31 - 1), "kind": kind,
                    "n": rng.randint(max_n // 2, max_n),
                    "special": rng.randint(0, max_n // 20) if kind == "mixed" else 0,
                    "q": 400})
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (cnt, m)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(cnt, m, rng)))
