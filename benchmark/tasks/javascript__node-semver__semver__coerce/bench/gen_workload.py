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
# Workload for coerce(version, options). Each case: {"v": input, "rtl": bool|null}.
# Inputs: strings (most), plus numbers, null, objects ({"$obj":1}) and parsed SemVer objects ({"$semver": v}).
def r(text, n):
    return text * n


FIXED = [None, {"$obj": 1}, "", ".", "version one", r("9", 16), r("1", 17), "a" + r("9", 16), r("1", 17) + "a",
         r("9", 16) + ".4.7.4", r("1", 16) + "." + r("9", 16) + "." + r("3", 16), {"$semver": "1.2.3"},
         ".1", ".1.", "..1", ".1.1", "1.", "1.0", "0", "0.1", "1.2.3.4", "35.12.18.24", "v1.2", " 1", "1 0",
         "1.1-1", "a1a", "version1.1", "42.6.7.9.3-alpha", "v3.4 replaces v3.3.1", r("1", 17) + ".2",
         "1." + r("2", 17) + ".3", "1.2." + r("3", 17) + ".4", "11" + r(".1", 126), r("1", 16) + ".2.3.4",
         "1.2.3." + r("4", 1024), r("1", 17) + ".4.7.4", 10, 1.5, "1.2.3/a/b/c/2.3.4", "1.2.3.4.5.6",
         "1.2.3.4.5/6", "1.2.3.4./6", "1.2.3/6", "1.2.3.4xyz", "x1.2.3.4.5.6.7.8.9", "1.2.3.4.5.6.7.8.9.10.11",
         "1.2.3.4 9.8.7.6", "v1-2-3", "no digits at all"]
WORDS = ["release", "notes", "build", "version", "v", "the", "lib", "-", "/", "_", ":", " ", ".", "rc", "x", "alpha"]
# (cases, mean text length)
SCALE = {"S": (300, 40), "M": (300, 400), "L": (300, 4000)}


def chunk(rng):
    r_ = rng.random()
    if r_ < 0.55:
        return rng.choice(WORDS)
    if r_ < 0.75:
        return ".".join(nid(rng) for _ in range(rng.randint(1, 5)))
    if r_ < 0.85:
        return rng.choice(["v", "V", "=", "@", ""]) + ver(rng)
    if r_ < 0.95:
        return r(rng.choice("0123456789"), rng.randint(15, 20))
    return "".join(rng.choice("abcxyz0123456789.") for _ in range(rng.randint(3, 12)))


def text(rng, n):
    out, ln = [], 0
    while ln < n:
        c = chunk(rng)
        out.append(c)
        ln += len(c)
    s = "".join(out)
    if rng.random() < 0.3:  # first digits appear only near the end
        s = "".join(ch for ch in s if not ch.isdigit()) + ver(rng)
    return s


def make(size, rng):
    n, mean = SCALE[size]
    cases = []
    if size == "S":
        for v in FIXED:
            for rtl in (None, True):
                cases.append({"v": v, "rtl": rtl})
    for _ in range(n):
        cases.append({"v": text(rng, rng.randint(mean // 2, mean * 3 // 2)), "rtl": rng.choice([None, False, True, True])})
    return cases


if __name__ == "__main__":
    write(sys.argv[1], ["S", "M", "L"], make)
