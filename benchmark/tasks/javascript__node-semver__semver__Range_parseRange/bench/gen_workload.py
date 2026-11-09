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
RANGE_FIXED = ["1.0.0 - 2.0.0", "1.0.0", ">=*", "", "*", "1", ">= 1.0.0", "<\t2.0.0", "0.1.20 || 1.2.4", "||",
               ">=0.2.3 || <0.0.1", "2.x.x", "1.2.x || 2.x", "x", "2.*.*", "~>3.2.1", "~> 1", "~ 1.0", "^0", "^ 1",
               "^0.1", "^0.0.1-beta", "^1.2.3-beta.4", "< 1.2", ">01.02.03", "~1.2.3beta", "^ 1.2 ^ 1", "1 2",
               "1.2 - 3.4.5", "1.2.3 - 3.4", "1.2.3 - 3", ">*", "<*", "^1.2.3+build", "1.2.3pre+asdf - 2.4.3-pre+asdf",
               "~1.2.1 =1.2.3", "<=0.7.x", "=0.7.x", ">1.2", "<0.7.x", "~0.0.1", "^0.0.1", "^x", "x - 1.0.0", "1.x - x",
               "blerg", "git+https://user:password0123@github.com/foo", ">=1.2.3 garbage", "~1.02.03beta", ">=01.02.03",
               "1.3.0 || <1.0.0 >2.0.0", "<1.6.16 || >=1.7.0 <1.7.11 || >=1.8.0 <1.8.2", "~ 1.0.3alpha", "  1.2.3  ",
               ">=1.2.7 <1.3.0", "1.2.7 || >=1.2.9 <2.0.0", ">= v1.2.3", "~1.2.3-alpha.1 || ^2.0.0-0"]
# Workload for Range.prototype.parseRange. Each case: {"r": one comparator set (no "||"), "o": options|null}.
# The driver calls rangeObj.parseRange(r) on a pre-built Range('*', o) receiver.
# (cases, comparators per set) -> about 2 / 30 / 300 comparators per call
SCALE = {"S": (300, (1, 4)), "M": (150, (20, 40)), "L": (150, (200, 400))}
OPTS = [None, None, True, {"loose": True}, {"includePrerelease": True}]


def make(size, rng):
    cnt, (lo, hi) = SCALE[size]
    cases = []
    if size == "S":
        for r in RANGE_FIXED:
            for part in r.split("||"):
                for o in (None, True, {"includePrerelease": True}):
                    cases.append({"r": part, "o": o})
    for _ in range(cnt):
        n = rng.randint(lo, hi)
        r = comp_set(rng, n)
        if rng.random() < 0.2:
            r = rng.choice([" ", "  ", "\t"]) + r + rng.choice(["", " "])
        cases.append({"r": r, "o": rng.choice(OPTS)})
    return cases


if __name__ == "__main__":
    write(sys.argv[1], ["S", "M", "L"], make)
