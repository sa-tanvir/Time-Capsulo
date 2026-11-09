"""Seeded workload generator for mux matchMapWithString. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# size: (cases, entries in toCheck, values per toMatch key)
SIZES = {"S": (4_000, 3, 2), "M": (400, 30, 6), "L": (40, 300, 20)}
PARTS = ["x", "content", "type", "accept", "requested", "with", "forwarded", "for", "api", "key", "trace", "id",
         "user", "agent", "cache", "control", "origin", "auth", "token", "lang"]

def canon(k):
    return "-".join(p[:1].upper() + p[1:].lower() for p in k.split("-"))

def rkey(rng, i):
    return "-".join(rng.choice(PARTS) for _ in range(rng.randint(1, 3))) + "-" + str(i)

def rval(rng):
    return "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789/;=.") for _ in range(rng.randint(1, 16)))

def case(rng, n, vk):
    canonical = rng.random() < 0.7
    check, match = [], {}
    for i in range(n):
        k = rkey(rng, i)
        if rng.random() < 0.5:
            k = k.upper() if rng.random() < 0.3 else k
        mk = canon(k) if canonical else k
        vals = [rval(rng) for _ in range(rng.randint(1, vk))]
        v = "" if rng.random() < 0.2 else rng.choice(vals)
        check.append([k, v])
        match[mk] = vals
    for i in range(n):                                   # unrelated extra keys
        match[canon(rkey(rng, 1000 + i))] = [rval(rng)]
    r = rng.random()
    if r < 0.15 and check:                              # a value that is not present
        j = rng.randrange(len(check)); check[j][1] = "missing-" + rval(rng)
    elif r < 0.3 and check:                             # a key that is not present
        j = rng.randrange(len(check)); check[j][0] = "absent-" + check[j][0]
    elif r < 0.4 and check:                             # key exists with an empty value list
        j = rng.randrange(len(check)); match[canon(check[j][0]) if canonical else check[j][0]] = []
    elif r < 0.45 and canonical:                        # flip canonicalization off: lookups use raw keys
        canonical = False
    return {"canon": canonical, "check": check, "match": sorted(match.items())}

EDGE = [
    {"canon": True, "check": [["x-requested-with", "XMLHttpRequest"]], "match": [["X-Requested-With", ["XMLHttpRequest"]]]},
    {"canon": True, "check": [["x-requested-with", ""]], "match": [["X-Requested-With", ["anything"]]]},
    {"canon": True, "check": [["x-requested-with", "XMLHttpRequest"]], "match": []},
    {"canon": False, "check": [["x-requested-with", "a"]], "match": [["X-Requested-With", ["a"]]]},
    {"canon": False, "check": [["foo", "bar"], ["baz", "ding"]], "match": [["foo", ["bar"]], ["baz", ["dong"]]]},
    {"canon": False, "check": [["foo", "bar"], ["baz", "ding"]], "match": [["foo", ["x", "bar"]], ["baz", ["ding"]]]},
    {"canon": True, "check": [], "match": []},
    {"canon": True, "check": [["k", ""]], "match": [["K", []]]},
    {"canon": True, "check": [["Foo", "ba[zr]"]], "match": [["Foo", ["bar"]]]},
]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k, vk)) in enumerate(SIZES.items()):
        rng = random.Random(20190125 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append(case(rng, k, vk))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
