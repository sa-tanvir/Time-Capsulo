"""Seeded workload generator (node-semver). Usage: python3 gen_workload.py <out_dir>"""
# ---- shared helpers for node-semver workloads (stdlib only) ----
import json, random, sys
from pathlib import Path

RELEASE = 20190724
PRE_WORDS = ["alpha", "beta", "rc", "pre", "dev", "next", "canary", "x-y", "r2", "R2", "foo", "Foo", "a", "b", "0a"]
BUILD_WORDS = ["build", "001", "sha", "x7", "exp", "0", "1", "20190724"]


def nid(rng):
    r = rng.random()
    if r < 0.5:
        return str(rng.randint(0, 9))
    if r < 0.85:
        return str(rng.randint(10, 99))
    return str(rng.randint(100, 20191))


def pre_ident(rng):
    return nid(rng) if rng.random() < 0.45 else rng.choice(PRE_WORDS)


def pre(rng, n):
    return ".".join(pre_ident(rng) for _ in range(n))


def ver(rng, pre_p=0.25, build_p=0.1, pre_n=(1, 3)):
    s = "%s.%s.%s" % (nid(rng), nid(rng), nid(rng))
    if rng.random() < pre_p:
        s += "-" + pre(rng, rng.randint(*pre_n))
    if rng.random() < build_p:
        s += "+" + ".".join(rng.choice(BUILD_WORDS) for _ in range(rng.randint(1, 2)))
    return s


def partial(rng):
    k = rng.choice([1, 2, 3, 3, 3])
    parts = [nid(rng) for _ in range(k)]
    if rng.random() < 0.3:
        j = rng.randint(0, k - 1)
        for q in range(j, k):
            parts[q] = rng.choice(["x", "*", "X"])
    s = ".".join(parts)
    if k == 3 and "x" not in s.lower() and "*" not in s and rng.random() < 0.2:
        s += "-" + pre(rng, rng.randint(1, 2))
    return s


def atom(rng):
    r = rng.random()
    sp = rng.choice(["", "", "", " "])
    if r < 0.4:
        op = rng.choice([">=", ">", "<", "<=", "=", ""])
        return op + (sp if op else "") + (ver(rng) if rng.random() < 0.6 else partial(rng))
    if r < 0.6:
        return rng.choice(["~", "~>"]) + sp + partial(rng)
    if r < 0.8:
        return "^" + sp + partial(rng)
    if r < 0.97:
        return partial(rng)
    return rng.choice(["*", "x", ">=*", "<*"])


def comp_set(rng, n):
    if n <= 2 and rng.random() < 0.15:
        return partial(rng) + " - " + partial(rng)
    return " ".join(atom(rng) for _ in range(n))


def range_str(rng, nsets, ncomp):
    return rng.choice([" || ", "||", " ||  "]).join(comp_set(rng, rng.randint(1, ncomp)) for _ in range(nsets))


def write(out_dir, sizes, make):
    out_dir = Path(out_dir)
    for i, size in enumerate(sizes):
        rng = random.Random(RELEASE + i)
        (out_dir / ("workload_%s.json" % size)).write_text(json.dumps(make(size, rng)))
# ---- task-specific part ----
# Workload for outside(version, range, hilo, options). Each case: {"v": version, "r": range, "h": hilo, "o": options|null}
# options is either a boolean (loose) or {"loose":..,"includePrerelease":..}.
FIXED = [("~1.2.2", "1.3.0", None), ("~0.6.1-1", "0.7.1-1", None), ("1.0.0 - 2.0.0", "2.0.1", None),
         ("1.0.0", "1.0.1-beta1", None), ("<=2.0.0", "2.1.1", None), ("0.1.20 || 1.2.4", "1.2.5", None),
         ("1.2.x || 2.x", "3.0.0", None), ("~> 1", "3.2.3", None), ("1", "2.0.0beta", True), ("<1", "1.0.0beta", True),
         ("~v0.5.4-pre", "0.6.1-pre", None), ("=0.7.x", "0.8.0-asdf", None), ("<0.7.x", "0.7.0", None),
         ("~0.6.1-1", "0.6.1-1", None), ("1.0.0 - 2.0.0", "0.9.9", None), (">=*", "0.2.4", None), ("", "1.0.0", True),
         ("*", "v1.2.3-foo", None), ("*", "v1.2.3-foo", True), (">=1.0.0", "1.1.0", None), ("<=2.0.0", "0.2.9", None),
         ("^0.1.0 || ~3.0.1 || 5.0.0", "3.2.0", None), ("^0.1.0 || ~3.0.1 || 5.0.0", "1.0.0beta", True),
         ("^0.1.0 || ~3.0.1 || >4 <=5.0.0", "3.5.0", None), ("^1.0.0alpha", "1.0.0beta", True),
         ("~1.0.0-alpha", "1.0.0-beta", None), ("=0.1.0", "1.0.0", None), (">1.0.0 <2.0.0", "3.0.0", None),
         (">=1.0.0 <2.0.0 || >3", "2.5.0", None), (">2.0.0", "1.0.0", None), ("<1.0.0", "2.0.0", None),
         ("1.2.3 >1.0.0", "0.1.0", None), ("1.2.3", "1.2.2", None), ("blerg", "1.2.3", None), ("1.2.3", "glorp", None)]
# (cases, number of || sets, max comparators per set)
SCALE = {"S": (200, 2, 3), "M": (200, 6, 8), "L": (200, 30, 20)}


def make(size, rng):
    cnt, nsets, ncomp = SCALE[size]
    cases = []
    if size == "S":
        for r, v, loose in FIXED:
            for h in ("<", ">"):
                cases.append({"v": v, "r": r, "h": h, "o": loose})
        cases.append({"v": "1.2.3", "r": ">1.5.0", "h": "blerg", "o": True})
    for _ in range(cnt):
        o = rng.choice([None, None, False, {"includePrerelease": True}, {"loose": False}])
        cases.append({"v": ver(rng, pre_p=0.2), "r": range_str(rng, rng.randint(1, nsets), ncomp),
                      "h": rng.choice(["<", ">"]), "o": o})
    return cases


if __name__ == "__main__":
    write(sys.argv[1], ["S", "M", "L"], make)
