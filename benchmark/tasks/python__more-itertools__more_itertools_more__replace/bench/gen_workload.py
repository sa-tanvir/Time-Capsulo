"""Seeded workload generator for replace(). Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (40, 300), "M": (60, 4_000), "L": (60, 40_000)}   # (cases, max sequence length)

def case(rng, max_len):
    length = rng.randint(1, max_len)
    alpha = rng.choice([2, 3, 5, 10])
    seq = [rng.randrange(alpha) for _ in range(length)]
    w = rng.choice([1, 1, 2, 3, 4, 6])
    kind = rng.choice(["pattern", "pattern", "first"]) if w > 1 else "member"
    if kind == "pattern":
        arg = [rng.randrange(alpha) for _ in range(w)]
    elif kind == "first":
        arg = rng.randrange(alpha)
    else:
        arg = rng.sample(range(alpha), rng.randint(1, max(1, alpha // 2)))
    return {"seq": seq, "w": w, "kind": kind, "arg": arg,
            "subs": [rng.randint(100, 110) for _ in range(rng.choice([0, 0, 1, 2, 4]))],
            "count": rng.choice([None, None, None, 0, 1, 3, 50])}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, m) for _ in range(n)]))
