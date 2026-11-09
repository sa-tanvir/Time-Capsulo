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
# Workload for SemVer.prototype.inc. Each case: {"v": version, "loose": bool, "pre": list|null, "rel": release, "id": identifier|null}
# The driver builds `new SemVer(v, loose)`, replaces its prerelease array by `pre` when given, then calls inc(rel, id).
RELS = ["prerelease"] * 6 + ["pre"] * 2 + ["major", "minor", "patch", "premajor", "preminor", "prepatch"]
FIXED = [  # from the test suite
    ("1.2.3", "major", None, False), ("1.2.3tag", "major", None, True), ("1.2.3-tag", "major", None, False),
    ("1.2.3", "fake", None, False), ("1.2.0-0", "patch", None, False), ("1.2.3-4", "minor", None, False),
    ("1.2.3-alpha.0.beta", "patch", None, False), ("1.2.4", "prerelease", None, False),
    ("1.2.3-alpha.10.beta.2", "prerelease", None, False), ("1.2.3-alpha.9.beta", "prerelease", None, False),
    ("1.2.0-1", "prepatch", None, False), ("1.2.3-1", "preminor", None, False), ("1.2.3-1", "premajor", None, False),
    ("1.2.0-1", "minor", None, False), ("1.0.0-1", "major", None, False), ("1.2.4", "prerelease", "dev", False),
    ("1.2.3-alpha.0", "prerelease", "dev", False), ("1.2.3-alpha.0", "prerelease", "alpha", False),
    ("1.2.3-alpha.10.beta.0", "prerelease", "alpha", False), ("1.2.3-dev.bar", "prerelease", "dev", False),
    ("1.2.0", "premajor", "dev", False), ("1.2.3", "pre", None, False), ("1.2.3-beta", "pre", None, False),
    ("1.2.3-beta", "pre", "beta", False), ("1.2.3-beta.x", "pre", "beta", False), ("1.2.3", "patch", "dev", False),
    ("1.2.3", "", None, False), ("1.2.3-a.b", "prerelease", None, False),
]
# per-case prerelease length (the "pre"/"prerelease" bumps scale with it)
SCALE = {"S": (300, 0, 4), "M": (300, 15, 45), "L": (300, 150, 450)}


def long_pre(rng, n):
    out = []
    for _ in range(n):
        if rng.random() < 0.1:
            out.append(rng.randint(0, 99))
        else:
            out.append(rng.choice(PRE_WORDS))
    if rng.random() < 0.5:  # numeric only near the front: forces a long scan
        out = [x if isinstance(x, str) else "id%d" % x for x in out]
        if rng.random() < 0.7:
            out[0] = rng.randint(0, 9)
    return out


def make(size, rng):
    n, lo, hi = SCALE[size]
    cases = []
    if size == "S":
        for v, rel, ident, loose in FIXED:
            cases.append({"v": v, "loose": loose, "pre": None, "rel": rel, "id": ident})
    for _ in range(n):
        p = None
        if hi > 4:
            p = long_pre(rng, rng.randint(lo, hi)) if rng.random() < 0.9 else []
            v = ver(rng, pre_p=0.0, build_p=0.1)
        else:
            v = ver(rng, pre_p=0.7, pre_n=(1, 4))
        ident = None
        r = rng.random()
        if r < 0.3:
            ident = rng.choice(PRE_WORDS)
        elif r < 0.45 and p:
            ident = p[0] if isinstance(p[0], str) else "alpha"
        cases.append({"v": v, "loose": False, "pre": p, "rel": rng.choice(RELS), "id": ident})
    return cases


if __name__ == "__main__":
    write(sys.argv[1], ["S", "M", "L"], make)
