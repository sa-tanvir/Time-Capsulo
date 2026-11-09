"""Seeded workload generator for mux matchMapWithRegex. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# size: (cases, entries in toCheck, values per toMatch key)
SIZES = {"S": (4_000, 3, 2), "M": (400, 30, 6), "L": (40, 300, 20)}
PARTS = ["x", "content", "type", "accept", "requested", "with", "forwarded", "for", "api", "key", "trace", "id",
         "user", "agent", "cache", "control", "origin", "auth", "token", "lang"]
MEDIA = ["text/html", "text/plain", "application/json", "application/xml", "application/xhtml+xml", "image/png",
         "https://example.co", "https://example.co.uk", "gzip", "deflate", "en-US", "fr"]

def canon(k):
    return "-".join(p[:1].upper() + p[1:].lower() for p in k.split("-"))

def rkey(rng, i):
    return "-".join(rng.choice(PARTS) for _ in range(rng.randint(1, 3))) + "-" + str(i)

def rval(rng):
    if rng.random() < 0.5:
        return rng.choice(MEDIA)
    return "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789/;=.") for _ in range(rng.randint(1, 16)))

def pattern_for(rng, s):
    r = rng.random()
    if r < 0.25:
        return None                                    # nil regexp: presence only
    if r < 0.45:
        return "^" + "".join("\\" + c if c in ".+?*()[]{}|^$\\" else c for c in s) + "$"
    if r < 0.7:
        a = rng.randrange(len(s)); b = rng.randint(a + 1, len(s))
        return "".join("\\" + c if c in ".+?*()[]{}|^$\\" else c for c in s[a:b])
    if r < 0.85:
        return "(?:html|json|xml)"
    return "^[a-z]+/[a-z+]+$"

def case(rng, n, vk):
    canonical = rng.random() < 0.7
    check, match = [], {}
    for i in range(n):
        k = rkey(rng, i)
        if rng.random() < 0.15:
            k = k.upper()
        mk = canon(k) if canonical else k
        vals = [rval(rng) for _ in range(rng.randint(1, vk))]
        check.append([k, pattern_for(rng, rng.choice(vals))])
        match[mk] = vals
    for i in range(n):
        match[canon(rkey(rng, 1000 + i))] = [rval(rng)]
    r = rng.random()
    if r < 0.15 and check:
        j = rng.randrange(len(check)); check[j][1] = "^missing-value$"
    elif r < 0.3 and check:
        j = rng.randrange(len(check)); check[j][0] = "absent-" + check[j][0]
    elif r < 0.4 and check:
        j = rng.randrange(len(check)); match[canon(check[j][0]) if canonical else check[j][0]] = []
    elif r < 0.45 and canonical:
        canonical = False
    return {"canon": canonical, "check": check, "match": sorted(match.items())}

EDGE = [
    {"canon": True, "check": [["Accept", "html"]], "match": [["Accept", ["text/plain", "text/html"]]]},
    {"canon": True, "check": [["Accept", "html"]], "match": [["Accept", ["application/xhtml+xml"]]]},
    {"canon": True, "check": [["Origin", "^https://example.co$"]], "match": [["Origin", ["https://example.co"]]]},
    {"canon": True, "check": [["Origin", "^https://example.co$"]], "match": [["Origin", ["https://example.co.uk"]]]},
    {"canon": True, "check": [["foo", "ba[zr]"]], "match": [["Foo", ["baz"]]]},
    {"canon": True, "check": [["foo", "ba[zr]"]], "match": [["Foo", ["bat"]]]},
    {"canon": True, "check": [["foo", ""]], "match": [["Foo", ["anything"]]]},
    {"canon": True, "check": [["foo", ""]], "match": [["Foo", []]]},
    {"canon": True, "check": [["foo", None]], "match": [["Foo", []]]},
    {"canon": True, "check": [["foo", None]], "match": []},
    {"canon": False, "check": [["foo", "x"]], "match": [["Foo", ["x"]]]},
    {"canon": False, "check": [], "match": []},
]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k, vk)) in enumerate(SIZES.items()):
        rng = random.Random(20190125 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append(case(rng, k, vk))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
