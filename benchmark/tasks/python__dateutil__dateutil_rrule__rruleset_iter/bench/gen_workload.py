"""Seeded workload generator for rruleset._iter. Usage: python3 gen_workload.py <out_dir>

Each case describes one rruleset: {"rrules": [rule...], "rdates": [h...], "exrules": [rule...],
"exdates": [h...]} where times are integer hour offsets from 2000-01-01T00:00 and a rule is
{"freq": "HOURLY"|"DAILY"|"WEEKLY", "start": h, "interval": n, "count": n, "byhour": [..] or null}.
All rules have a COUNT so every set is finite. Total occurrences per case grow ~10x per size.
"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (30, 100), "M": (20, 1000), "L": (20, 10000)}   # (cases, target occurrences per case)


def rule(rng, span, count):
    freq = rng.choice(["HOURLY", "HOURLY", "HOURLY", "DAILY", "DAILY", "WEEKLY"])
    r = {"freq": freq, "start": rng.randint(0, max(0, span // 4)), "interval": rng.choice([1, 1, 2, 3, 5]),
         "count": max(1, count), "byhour": None}
    if freq != "HOURLY" and rng.random() < 0.5:
        r["byhour"] = sorted(rng.sample(range(24), rng.randint(1, 6)))
    return r


def case(rng, target):
    kind = rng.random()
    span = target * rng.choice([1, 2, 3])
    n_rr = rng.choice([0, 1, 1, 2, 3, 5]) if kind > 0.1 else 0
    rrules = []
    if n_rr:
        per = max(1, target // n_rr)
        rrules = [rule(rng, span, rng.randint(per // 2 + 1, per)) for _ in range(n_rr)]
    n_rd = rng.randint(0, target // 2) if n_rr else rng.randint(1, target)
    rdates = [rng.randint(0, span) for _ in range(n_rd)]
    n_ex = rng.choice([0, 0, 1, 2])
    exrules = [rule(rng, span, rng.randint(1, max(1, target // 3))) for _ in range(n_ex)]
    n_xd = rng.randint(0, target // 3)
    exdates = [rng.randint(-5, span + 5) for _ in range(n_xd)]
    return {"rrules": rrules, "rdates": rdates, "exrules": exrules, "exdates": exdates}


def fixed():
    out = [
        {"rrules": [], "rdates": [], "exrules": [], "exdates": []},
        {"rrules": [], "rdates": [], "exrules": [], "exdates": [1, 2, 3]},
        {"rrules": [], "rdates": [5, 3, 5, 1], "exrules": [], "exdates": []},
        {"rrules": [], "rdates": [5, 3, 5, 1], "exrules": [], "exdates": [5]},
        {"rrules": [{"freq": "HOURLY", "start": 0, "interval": 1, "count": 10, "byhour": None}],
         "rdates": [], "exrules": [{"freq": "HOURLY", "start": 0, "interval": 1, "count": 10, "byhour": None}],
         "exdates": []},
        {"rrules": [{"freq": "HOURLY", "start": 0, "interval": 2, "count": 10, "byhour": None},
                    {"freq": "HOURLY", "start": 0, "interval": 3, "count": 10, "byhour": None}],
         "rdates": [0, 6, 7, 100], "exrules": [], "exdates": [100, -1, 12, 12, 7]},
        {"rrules": [{"freq": "DAILY", "start": 0, "interval": 1, "count": 6, "byhour": [9]}],
         "rdates": [], "exrules": [{"freq": "DAILY", "start": 48, "interval": 2, "count": 3, "byhour": [9]}],
         "exdates": [9]},
    ]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, target)) in enumerate(SIZES.items()):
        rng = random.Random(20191103 + i)
        cs = fixed() if size == "S" else []
        while len(cs) < n:
            cs.append(case(rng, target))
        (out_dir / ("workload_%s.json" % size)).write_text(json.dumps(cs))
