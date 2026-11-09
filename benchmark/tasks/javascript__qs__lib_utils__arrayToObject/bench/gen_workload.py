"""Seeded workload generator for utils.arrayToObject. Usage: python3 gen_workload.py <out_dir>

Each case is {"base": [...], "len": N, "undef": k, "holes": m, "opts": <options or null>}.
The driver builds an array of length N cycling through `base`; every element whose index i satisfies
k > 0 and i % k == k - 1 is set to undefined, and every index with m > 0 and i % m == 0 is deleted (hole).
Base elements may be {"$undef": 1}, which the driver turns into undefined.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20191108
# (number of random cases, max array length): per-case length grows ~10x per size step
SIZES = {"S": (300, 200), "M": (300, 2_000), "L": (300, 20_000)}

OPTS = [None, None, {}, {"plainObjects": True}, {"plainObjects": False}, {"plainObjects": 1},
        {"plainObjects": True, "allowPrototypes": True}, {"allowPrototypes": True}]


def elem(rng):
    r = rng.random()
    if r < 0.35:
        return "".join(rng.choice("abcxyz09 &=") for _ in range(rng.randint(0, 6)))
    if r < 0.55:
        return rng.randint(-1000, 1000)
    if r < 0.62:
        return None
    if r < 0.67:
        return rng.choice([True, False, 0, ""])
    if r < 0.75:
        return {"$undef": 1}
    if r < 0.88:
        return {"k" + str(rng.randint(0, 9)): rng.randint(0, 9)}
    return [rng.randint(0, 9) for _ in range(rng.randint(0, 3))]


FIXED = [
    {"base": [], "len": 0, "undef": 0, "holes": 0, "opts": None},
    {"base": [], "len": 0, "undef": 0, "holes": 0, "opts": {"plainObjects": True}},
    {"base": ["a", "b"], "len": 2, "undef": 0, "holes": 0, "opts": None},
    {"base": ["bar"], "len": 1, "undef": 0, "holes": 0, "opts": {}},
    {"base": ["b"], "len": 1, "undef": 0, "holes": 0, "opts": {"plainObjects": True}},
    {"base": ["b"], "len": 3, "undef": 0, "holes": 0, "opts": None},
    {"base": [None, {"$undef": 1}, 0], "len": 3, "undef": 0, "holes": 0, "opts": None},
    {"base": ["x"], "len": 3, "undef": 0, "holes": 3, "opts": None},
    {"base": ["x", "y"], "len": 5, "undef": 2, "holes": 0, "opts": {"plainObjects": True}},
    {"base": [{"$undef": 1}], "len": 4, "undef": 0, "holes": 0, "opts": None},
]


def cases(n, max_len, rng, with_fixed):
    out = list(FIXED) if with_fixed else []
    for _ in range(n):
        base = [elem(rng) for _ in range(rng.randint(1, 12))]
        out.append({
            "base": base,
            "len": rng.randint(0, max_len),
            "undef": rng.choice([0, 0, 2, 3, 7, 50]),
            "holes": rng.choice([0, 0, 0, 2, 5, 11]),
            "opts": rng.choice(OPTS),
        })
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, m, rng, size == "S")))
