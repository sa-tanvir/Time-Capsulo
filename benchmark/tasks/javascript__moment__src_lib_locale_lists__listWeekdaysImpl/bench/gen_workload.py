"""Seeded workload generator for listWeekdaysImpl(localeSorted, format, index, field)
(backs moment.weekdays / weekdaysShort / weekdaysMin).
Usage: python3 gen_workload.py <out_dir>

Each case is [locale, field, args] with args = the first three arguments, in the shapes the public
listers accept: (), (index), (bool), (bool, index), (bool, format), (bool, format, index), plus
null/undefined/number first arguments. Locales: 'en' and three driver-defined test locales.
Indexes are integers (including negative and >= 7). Per-call work is bounded (at most 7 names), so
S/M/L scale the number of calls (300 / 3,000 / 30,000), sorted by locale.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
SIZES = {"S": 300, "M": 3000, "L": 30000}
LOCALES = ["en", "tc-num", "tc-fmt", "tc-fn"]
FIELDS = ["weekdays", "weekdaysShort", "weekdaysMin"]
FORMATS = ["dddd", "ddd", "dd", "[On] dddd", "[on last] dddd", "-ddd-", "D MMMM", "", "dddd [on]"]
U = {"$undef": 1}

FIXED_ARGS = [[], [0], [2], [6], [7], [-1], [True], [False], [True, 0], [False, 2], [True, 2], [True, "dddd"],
              [True, "[On] dddd"], [True, "[On] dddd", 3], [False, "-ddd-", 4], [True, U, 5], [None], [U],
              [True, None], [False, ""], [10], [True, -3], [False, "dddd", -8]]


def args(rng):
    r = rng.random()
    idx = rng.choice([rng.randint(0, 6), rng.randint(0, 6), rng.randint(-10, 20)])
    if r < 0.15:
        return []
    if r < 0.3:
        return [idx]
    if r < 0.4:
        return [rng.choice([None, U])]
    b = rng.random() < 0.6
    r = rng.random()
    if r < 0.25:
        return [b]
    if r < 0.5:
        return [b, idx]
    if r < 0.75:
        return [b, rng.choice(FORMATS)]
    return [b, rng.choice(FORMATS + [None, U]), idx]


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, (size, n) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cases = []
        if size == "S":
            cases += [[loc, fld, a] for loc in LOCALES for fld in FIELDS for a in FIXED_ARGS]
        while len(cases) < n:
            cases.append([rng.choice(LOCALES), rng.choice(FIELDS), args(rng)])
        cases.sort(key=lambda c: LOCALES.index(c[0]))
        (out / f"workload_{size}.json").write_text(json.dumps(cases, separators=(",", ":")))
