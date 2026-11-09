"""Seeded workload generator for semver NewConstraint. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# size: (strings, (min, max) constraints per string, inner repetitions per pass)
SIZES = {"S": (5_000, (1, 3), 1), "M": (2_000, (5, 15), 1), "L": (400, (40, 90), 1)}
OPS = ["", "=", "!=", ">", "<", ">=", "=>", "<=", "=<", "~", "~>", "^"]
PRE = ["alpha", "beta.1", "rc.2", "0", "a-b", "SNAPSHOT.103", "x.Y.0"]
EDGE = [">= 1.1", ">40.50.60, < 50.70", "2.0", "v2.3.5-20161202202307-sha.e8fc5e5", ">= bar", "BAR >= 1.2.3",
        ">= 1.2.3 < 2.0", ">= 1.2.3 < 2.0 || => 3.0 < 4", ">= 1.2.3, < 2.0", ">= 1.2.3, < 2.0 || => 3.0, < 4",
        "3 - 4 || => 3.0, < 4", "*", ">=1.2.3", "2.x,   >=1.2.3 || >4.5.6, < 5.7",
        "2.x,   >=1.2.3 || >4.5.6, < 5.7 || >40.50.60, < 50.70", "1.2", "1.1 - 2", "1.5.0 - 4.5", "1.1-3",
        "~1.2.3-beta.2", "^0.2.3-beta.2", "!=4.1-alpha", "<1.x", "<=1.1.x", "~*", "~0.0.0", "0.x.x",
        ">=1.1    <2    !=1.2.3", ">= 1.1, <     2, !=1.2.3", "> 1.1    <3", ">1<2", "x.1.2-beta", "1.x.3",
        "v1.2.3+meta", ">=1.2.3,", ",>=1.2.3", "1.2 - 3.4 , 5 - 6", "||", ">=1 || ", "", " ", "foo",
        ">=1.2.3-01", "1.x-01", "99999999999999999999.0.0", ">= 1.2 || foo", "1 - 2 || foo", "~~1.2",
        "2 - 3, 4.0.0 - 5.1", "^1.2.x-alpha", "= 2.0", "4.1.x", "!=4.x", ">= 1.2.3 <2.0.0 || < 0.5 || ^3"]

def num(rng):
    return str(rng.choice([0, 1, 2, 3, rng.randint(0, 20), rng.randint(0, 999)]))

def ver(rng, allow_wild=True):
    w = rng.choice(["x", "X", "*"])
    if allow_wild and rng.random() < 0.06:
        return w
    k = rng.choice([1, 2, 3, 3, 3])
    parts = [num(rng) for _ in range(k)]
    if allow_wild and k > 1 and rng.random() < 0.25:
        parts[-1] = w
    s = ("v" if rng.random() < 0.05 else "") + ".".join(parts)
    if rng.random() < 0.15:
        s += "-" + rng.choice(PRE)
    if k == 3 and rng.random() < 0.03:
        s += "+build." + num(rng)
    return s

def term(rng):
    if rng.random() < 0.07:
        return ver(rng, False) + " - " + ver(rng, False)       # hyphen range
    return rng.choice(OPS) + rng.choice(["", "", " ", "  "]) + ver(rng)

def group(rng, k):
    out = term(rng)
    for _ in range(k - 1):
        out += rng.choice([", ", ",", " ", "  ", " , "]) + term(rng)
    return out

def bad(rng):
    return rng.choice(["foo", ">= bar", "~~1.2", "1.2.3-01", ">=1.2.3-alpha.01", "a.b.c", "!", "1.2.3_4", ">= 1.x-007"])

def case(rng, lo, hi):
    k = rng.randint(lo, hi)
    groups, left = [], k
    while left > 0:
        g = min(left, rng.randint(1, 6))
        groups.append(group(rng, g))
        left -= g
    if rng.random() < 0.04:
        groups[rng.randrange(len(groups))] = bad(rng)
    out = groups[0]
    for prev, g in zip(groups, groups[1:]):
        # '|' is part of the version character class, so "||" glued to a hyphen range would merge
        # the range's bound with the neighbouring group; keep spaces around "||" next to ranges.
        out += (" || " if " - " in prev or " - " in g else rng.choice([" || ", "||", " ||"])) + g
    return out

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, (lo, hi), inner)) in enumerate(SIZES.items()):
        rng = random.Random(20191213 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append(case(rng, lo, hi))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"inner": inner, "cases": cases}))
