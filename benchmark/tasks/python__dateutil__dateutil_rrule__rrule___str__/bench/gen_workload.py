"""Seeded workload generator for rrule.__str__. Usage: python3 gen_workload.py <out_dir>

Each case holds rrule constructor arguments. Per-case scale grows ~10x per size: each BYxxx list has up to K
values (bounded by the rule's value range; BYSETPOS, BYYEARDAY, BYEASTER and nth-weekday lists can reach K),
K = 3 (S), 30 (M), 300 (L)."""
import json, random, sys
from pathlib import Path

SIZES = {"S": (3, 3000), "M": (30, 2000), "L": (300, 1000)}   # (K, cases)
RANGES = {"bymonth": (1, 12), "bymonthday": (-31, 31), "byyearday": (-366, 366), "byweekno": (-53, 53),
          "bysetpos": (-366, 366), "byhour": (0, 23), "byminute": (0, 59), "bysecond": (0, 59),
          "byeaster": (-1000, 1000)}


def vals(rng, key, K):
    lo, hi = RANGES[key]
    out = [rng.randint(lo, hi) for _ in range(rng.randint(1, K))]
    out = [v for v in out if v != 0 or key in ("byhour", "byminute", "bysecond", "byeaster")]
    return out or [1]


def dt(rng):
    return [rng.randint(1970, 2100), rng.randint(1, 12), rng.randint(1, 28), rng.randint(0, 23),
            rng.randint(0, 59), rng.randint(0, 59)]


def case(rng, K):
    c = {"freq": rng.choice([0, 0, 1, 1, 2, 2, 3, 3, 4, 5, 6]), "dtstart": dt(rng),
         "aware": rng.random() < 0.15, "interval": rng.choice([1, 1, 1, 2, 3, 7, 52])}
    if rng.random() < 0.5:
        c["wkst"] = rng.randint(0, 6)
    r = rng.random()
    if r < 0.45:
        c["count"] = rng.randint(0, 50)
    elif r < 0.85:
        c["until"] = dt(rng)
    for key in RANGES:
        if key in ("byhour", "byminute", "bysecond") and c["freq"] >= 4:
            continue
        if rng.random() < 0.3:
            c[key] = vals(rng, key, K)
    if rng.random() < 0.4:
        wd = []
        for _ in range(rng.randint(1, K)):
            n = rng.choice([None, None, rng.randint(-53, 53)])
            wd.append([rng.randint(0, 6), n or None])
        c["byweekday"] = wd
    return c


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (K, n)) in enumerate(SIZES.items()):
        rng = random.Random(20190311 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": [case(rng, K) for _ in range(n)]}))
