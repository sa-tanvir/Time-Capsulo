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
# Workload for the Comparator constructor. Each case: {"c": comparator string, "o": options|null} or, in S only,
# {"cc": [comparator, options-of-existing-Comparator], "o": ...} (input is an existing Comparator).
# Per-case scale is the comparator length (a version is limited to 256 characters): ~12 / ~70 / ~230 chars.
FIXED = [">=1.2.3", "1.2.3", "=1.2.3", "", ">", "<", ">=", "<=", "=", ">= v1.2.3", "> 1.0.0", "<\t2.0.0", "<=   2.0.0",
         ">=1.2.3-beta.4+build.5", "v1.2.3", "=v1.2.3", ">=01.02.03", "1.2.3foo", "~1.2.3", "^1.2.3", "1.2", "1.2.x",
         "*", ">=*", "<0.0.0-0", ">=1.0.0-0", "<2.0.0-beta.01", " >=1.2.3", ">=1.2.3 ", "> =1.2.3", ">=  =1.2.3",
         "==1.2.3", "!1.2.3", "blerg", ">=1.2.3.4", ">=90071992547409910.0.0", ">=1.2.3-90071992547409910"]
SCALE = {"S": (400, 1, 2, 0), "M": (1500, 6, 14, 1), "L": (1500, 25, 45, 3)}


def long_ver(rng, lo, hi, nb):
    v = "%s.%s.%s" % (nid(rng), nid(rng), nid(rng))
    if hi:
        v += "-" + pre(rng, rng.randint(lo, hi))
    if nb:
        v += "+" + ".".join(rng.choice(BUILD_WORDS) for _ in range(rng.randint(nb, 3 * nb)))
    return v[:240].rstrip(".-+")


def make(size, rng):
    cnt, lo, hi, nb = SCALE[size]
    cases = []
    if size == "S":
        for c in FIXED:
            for o in (None, True, {"loose": False, "includePrerelease": True}):
                cases.append({"c": c, "o": o})
        for c in [">=1.2.3", "", "<2.0.0-pre"]:
            for o0 in (None, True):
                for o in (None, True, False, {"loose": True}):
                    cases.append({"cc": [c, o0], "o": o})
    for _ in range(cnt):
        op = rng.choice([">=", ">", "<", "<=", "=", "", ""])
        v = long_ver(rng, lo, hi, nb)
        loose = rng.random() < 0.3
        if loose and rng.random() < 0.5:
            v = rng.choice(["v", "=", " ", "v "]) + v
        o = rng.choice([True, {"loose": True}]) if loose else rng.choice([None, False, {"includePrerelease": True}])
        cases.append({"c": op + rng.choice(["", "", " "]) + v, "o": o})
    return cases


if __name__ == "__main__":
    write(sys.argv[1], ["S", "M", "L"], make)
