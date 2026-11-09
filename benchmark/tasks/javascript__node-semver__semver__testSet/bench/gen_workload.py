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
# Workload for testSet (module-private), reached through Range.prototype.test with pre-built SemVer objects.
# Each case: {"r": range, "o": options|null, "vs": [versions]}; the driver builds the Range and SemVer objects
# outside the timed region. Ranges have one or two long comparator sets, mostly wide bounds so that many
# versions satisfy all comparators and the prerelease rule is exercised.
FIXED = [("1.2.3-pre+asdf - 2.4.3-pre+asdf", ["1.2.3", "1.2.3-pre.2", "2.4.3-alpha", "2.4.3-pre", "2.4.4-pre"]),
         ("^1.2.3+build", ["1.2.3", "1.3.0", "2.0.0", "1.2.3-pre"]), ("*", ["1.0.0-rc1", "1.2.3"]),
         ("^1.0.0-rc2", ["1.0.0-rc3", "1.0.1-rc1", "1.0.0", "2.0.0"]), ("~v0.5.4-pre", ["0.5.5", "0.5.4", "0.5.4-pre.1", "0.5.5-a"]),
         ("<=1.2.3", ["1.2.3-beta"]), ("^1.2.3-alpha", ["1.2.3-pre", "1.2.4-pre", "1.2.2"]),
         (">=1.0.0-alpha <=1.0.0-beta.5 >0.9.9 <2", ["1.0.0-alpha.1", "1.0.0-beta.6", "1.0.0", "1.0.1-x"]),
         ("2.x", ["2.0.0-pre.0", "2.1.0-pre.0", "3.0.0-pre.0"]), (">=0.0.0 *", ["0.0.0-0", "1.0.0"])]
# (cases, comparators per set, versions per case)
SCALE = {"S": (120, (1, 6), 6), "M": (120, (30, 60), 6), "L": (120, (300, 600), 6)}


def wide_comp(rng):
    # bounds that every generated version (major 3..7) satisfies
    r = rng.random()
    if r < 0.4:
        return rng.choice([">=", ">"]) + "%d.%d.%d" % (rng.randint(0, 2), rng.randint(0, 9), rng.randint(0, 9))
    if r < 0.8:
        return rng.choice(["<=", "<"]) + "%d.%d.%d" % (rng.randint(8, 30), rng.randint(0, 9), rng.randint(0, 9))
    if r < 0.95:
        return rng.choice([">=", ">"]) + "%d.%d.%d-%s" % (rng.randint(0, 2), rng.randint(0, 9), rng.randint(0, 9), pre(rng, 1))
    return "*"


def comp_list(rng, n):
    comps = [wide_comp(rng) for _ in range(n)]
    if rng.random() < 0.25:  # one comparator that rejects, at a random position
        comps[rng.randrange(n)] = rng.choice(["<3.0.0", ">=8.0.0", "<=1.2.3", ">9.9.9-rc.1"])
    if rng.random() < 0.3:  # a prerelease comparator sharing major.minor.patch with some versions
        comps[rng.randrange(n)] = ">=%d.%d.%d-0" % (rng.randint(3, 7), rng.randint(0, 2), rng.randint(0, 2))
    return " ".join(comps)


def make(size, rng):
    cnt, (lo, hi), nv = SCALE[size]
    cases = []
    if size == "S":
        for r, vs in FIXED:
            for o in (None, {"includePrerelease": True}):
                cases.append({"r": r, "o": o, "vs": vs})
    for _ in range(cnt):
        sets = [comp_list(rng, rng.randint(lo, hi)) for _ in range(rng.randint(1, 2))]
        vs = ["%d.%d.%d" % (rng.randint(3, 7), rng.randint(0, 2), rng.randint(0, 2)) +
              ("-" + pre(rng, rng.randint(1, 2)) if rng.random() < 0.6 else "") for _ in range(nv)]
        cases.append({"r": " || ".join(sets), "o": rng.choice([None, None, {"includePrerelease": True}]), "vs": vs})
    return cases


if __name__ == "__main__":
    write(sys.argv[1], ["S", "M", "L"], make)
