"""Seeded workload generator for relativedelta.__add__. Usage: python3 gen_workload.py <out_dir>
Output: {"rds": [...], "others": [...], "cases": [[rd_index, other_index], ...]}
rd = [years, months, days, leapdays, hours, minutes, seconds, microseconds,
      year, month, day, weekday([w, n] or null), hour, minute, second, microsecond, yearday]
other = ["rd", rd] | ["td", days, seconds, us] | ["date", y, m, d] |
        ["dt", y, m, d, h, mi, s, us, tz_offset_minutes_or_null] | ["int", v] | ["str", v] | ["none"]"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (300, 2_000), "M": (3_000, 20_000), "L": (6_000, 200_000)}  # (pool, cases)


def maybe(rng, p, f):
    return f() if rng.random() < p else None


def num(rng, lo, hi, p=0.5):
    if rng.random() >= p:
        return 0
    if rng.random() < 0.08:
        return rng.choice([0.5, -0.5, 1.5, 0.25, 2.75])
    return rng.randint(lo, hi)


def rd(rng):
    r = [rng.randint(-40, 40) if rng.random() < 0.4 else 0,
         rng.randint(-30, 30) if rng.random() < 0.5 else 0,
         num(rng, -800, 800, 0.6),
         rng.choice([0, 0, 0, 1, -1]),
         num(rng, -50, 50, 0.3), num(rng, -200, 200, 0.25),
         num(rng, -5000, 5000, 0.25), rng.randint(-3_000_000, 3_000_000) if rng.random() < 0.2 else 0,
         maybe(rng, 0.15, lambda: rng.randint(1960, 2040)),
         maybe(rng, 0.2, lambda: rng.randint(1, 12)),
         maybe(rng, 0.25, lambda: rng.choice([1, 15, 28, 29, 30, 31, rng.randint(1, 31)])),
         maybe(rng, 0.3, lambda: [rng.randint(0, 6), rng.choice([None, None, 0, 1, 2, 3, -1, -2, -4])]),
         maybe(rng, 0.15, lambda: rng.randint(0, 23)), maybe(rng, 0.1, lambda: rng.randint(0, 59)),
         maybe(rng, 0.1, lambda: rng.randint(0, 59)), maybe(rng, 0.05, lambda: rng.randint(0, 999999)),
         None]
    if rng.random() < 0.04:   # yearday / nlyearday style deltas
        r = [0] * 8 + [None] * 8 + [rng.choice([1, -1]) * rng.randint(1, 366)]
    return r


def other(rng):
    r = rng.random()
    if r < 0.2:
        return ["rd", rd(rng)]
    if r < 0.3:
        return ["td", rng.randint(-2000, 2000), rng.randint(0, 86399), rng.randint(0, 999999)]
    if r < 0.55:
        return ["date", rng.randint(1950, 2050), rng.randint(1, 12), rng.randint(1, 28) if rng.random() < 0.6 else 28 + rng.randint(0, 3)]
    if r < 0.97:
        return ["dt", rng.randint(1950, 2050), rng.randint(1, 12), rng.randint(1, 28),
                rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59), rng.randint(0, 999999),
                rng.choice([None, None, None, 0, 60, -300, 330])]
    return rng.choice([["int", rng.randint(-9, 9)], ["str", "x"], ["none"]])


def fix_date(o):
    if o[0] == "date":   # keep the day valid for its month
        import calendar
        o[3] = min(o[3], calendar.monthrange(o[1], o[2])[1])
    return o


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (pool, n)) in enumerate(SIZES.items()):
        rng = random.Random(20191103 + i)
        rds = [rd(rng) for _ in range(pool)]
        others = [fix_date(other(rng)) for _ in range(pool)]
        cases = [[rng.randrange(pool), rng.randrange(pool)] for _ in range(n)]
        data = {"rds": rds, "others": others, "cases": cases}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(data, separators=(",", ":")))
