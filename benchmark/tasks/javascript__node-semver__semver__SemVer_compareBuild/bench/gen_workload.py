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
# Workload for SemVer.prototype.compareBuild. Each case: {"a": [version, build-list|null], "b": same, or "bs": version string}
# The driver builds SemVer objects (build array replaced by the list when given) outside the timed region;
# "bs" cases pass a plain string as `other`.
FIXED = [("1.0.0", "1.0.0+0"), ("1.0.0+0", "1.0.0+0"), ("1.0.0+0", "1.0.0"), ("1.0.0+0", "1.0.0+0.0"),
         ("1.0.0+0", "1.0.0+1"), ("1.0.0+1", "1.0.0+0"), ("1.0.0+1.0", "1.0.0+1"), ("1.2.3+build", "1.2.3+otherbuild"),
         ("1.2.3+10", "1.2.3+9"), ("1.2.3+a", "1.2.3+1"), ("1.2.3+001", "1.2.3+1"), ("1.2.3+01", "1.2.3+1"),
         ("1.2.3+B", "1.2.3+a"), ("9.9.9+x.y", "0.0.1+x.y"), ("1.2.3-pre+5", "1.2.3+5"), ("1.2.3+x-1", "1.2.3+x-1.0")]
SCALE = {"S": (400, 0, 6), "M": (400, 30, 90), "L": (400, 300, 900)}
BWORDS = BUILD_WORDS + ["sha.5114f85", "a", "B", "x-1", "0", "00", "007"]


def ident(rng):
    return str(rng.randint(0, 999)) if rng.random() < 0.5 else rng.choice(BWORDS)


def pair(rng, lo, hi):
    n = rng.randint(lo, hi)
    a = [ident(rng) for _ in range(n)]
    b = list(a)
    r = rng.random()
    if r < 0.15:
        pass
    elif r < 0.3 and n:
        b = b[:rng.randint(0, n - 1)]
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
        cases.append({"a": [ver(rng, build_p=0), a], "b": [ver(rng, build_p=0), b]})
    return cases


if __name__ == "__main__":
    write(sys.argv[1], ["S", "M", "L"], make)
