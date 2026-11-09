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
# Workload for SemVer.prototype.comparePre. Each case: {"a": [version, prerelease-list|null], "b": same, or "bs": version string}
# The driver builds SemVer objects (prerelease replaced by the list when given) outside the timed region;
# "bs" cases pass a plain string as `other`.
FIXED = [("1.2.3-alpha.0.pr.1", "9.9.9-alpha.0.pr.1"), ("1.2.3-alpha.0.pr.1", "1.2.3"), ("1.2.3", "1.2.3-a"),
         ("1.2.3", "2.0.0"), ("1.2.3-alpha.0.pr.1", "1.2.3-alpha.0.pr.2"), ("1.2.3-alpha.0.pr.1", "1.2.3-alpha.0.2"),
         ("1.2.3-a.b", "1.2.3-a"), ("1.2.3-a", "1.2.3-a.b"), ("1.2.3-r2", "1.2.3-r100"), ("1.2.3-r100", "1.2.3-R2"),
         ("1.2.3-5-foo", "1.2.3-5"), ("1.2.3-a.10", "1.2.3-a.5"), ("1.2.3-a.b.c.10.d.5", "1.2.3-a.b.c.5.d.100"),
         ("1.2.3-0", "1.2.3-0"), ("1.2.3-beta.90071992547409910", "1.2.3-beta.9"), ("1.2.3-1", "1.2.3-alpha")]
# per-case prerelease length (common prefix length dominates the cost)
SCALE = {"S": (400, 0, 6), "M": (400, 30, 90), "L": (400, 300, 900)}


def ident(rng):
    return rng.randint(0, 999) if rng.random() < 0.5 else rng.choice(PRE_WORDS)


def pair(rng, lo, hi):
    n = rng.randint(lo, hi)
    a = [ident(rng) for _ in range(n)]
    b = list(a)
    r = rng.random()
    if r < 0.15:
        pass  # equal
    elif r < 0.3 and n:
        b = b[:rng.randint(0, n - 1)]  # prefix
    elif r < 0.4:
        b.extend(ident(rng) for _ in range(rng.randint(1, 3)))
    elif n:
        k = rng.randint(n * 2 // 3, n - 1)
        b[k] = ident(rng)
    if rng.random() < 0.5:
        a, b = b, a
    return a, b


def make(size, rng):
    cnt, lo, hi = SCALE[size]
    cases = []
    if size == "S":
        for a, b in FIXED:
            cases.append({"a": [a, None], "b": [b, None]})
            cases.append({"a": [a, None], "bs": b})
    for _ in range(cnt):
        a, b = pair(rng, lo, hi)
        if rng.random() < 0.05:
            a = []
        if rng.random() < 0.05:
            b = []
        cases.append({"a": [ver(rng, pre_p=0, build_p=0), a], "b": [ver(rng, pre_p=0, build_p=0), b]})
    return cases


if __name__ == "__main__":
    write(sys.argv[1], ["S", "M", "L"], make)
