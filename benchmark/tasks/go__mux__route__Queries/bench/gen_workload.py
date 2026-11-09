"""Seeded workload generator for mux Route.Queries. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# size: (cases, key/value pairs per call)
SIZES = {"S": (3_000, 2), "M": (300, 20), "L": (30, 200)}
KEYS = ["foo", "bar", "baz", "id", "page", "q", "sort", "lang", "filter", "token"]

def value(rng, i):
    r = rng.random()
    if r < 0.3:
        return rng.choice(["bar", "ding", "1", "true", "json"])
    if r < 0.4:
        return ""
    if r < 0.7:
        return "{v%d}" % i
    if r < 0.85:
        return "{v%d:[0-9]+}" % i
    return rng.choice(["{v%d:[a-z]{2}}", "{v%d:(?:asc|desc)}", "x-{v%d}-y"]).replace("%d", str(i))

def case(rng, k):
    base = rng.choice(["", "host", "path", "both"])
    host = "{h}.example.com" if base in ("host", "both") else ""
    path = "/api/{p}" if base in ("path", "both") else ""
    pairs = []
    for i in range(k):
        pairs += [rng.choice(KEYS) + str(i), value(rng, i)]
    r = rng.random()
    if r < 0.04:
        pairs.append("dangling")                                   # odd number of strings
    elif r < 0.08:
        j = rng.randrange(k); pairs[2 * j + 1] = "{h}" if host else "{p}" if path else "{v0}{v0}"
    elif r < 0.10:
        j = rng.randrange(k); pairs[2 * j + 1] = "{broken"
    elif r < 0.12:
        j = rng.randrange(k); pairs[2 * j + 1] = "{x:[0-9}"
    elif r < 0.14:
        j = rng.randrange(k); pairs[2 * j + 1] = "{:[0-9]+}"
    return {"host": host, "path": path, "preerr": rng.random() < 0.02, "pairs": pairs}

EDGE = [
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "bar", "baz", "ding"]},
    {"host": "www.example.com", "path": "/api", "preerr": False, "pairs": ["foo", "bar", "baz", "ding"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "{v1}"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "{v1}", "baz", "{v2}"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "{v1:[0-9]+}"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "{v1:[0-9]{1}(?:a|b)}"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "{v-1}", "baz", "{v-2}"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", ""]},
    {"host": "", "path": "", "preerr": False, "pairs": []},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "bar", "baz"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "{v1}", "bar", "{v1}", "baz", "x"]},
    {"host": "{v1}.example.com", "path": "", "preerr": False, "pairs": ["foo", "{v1}"]},
    {"host": "", "path": "/{v1}", "preerr": False, "pairs": ["a", "1", "foo", "{v1}", "b", "2"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "{bar", "baz", "1"]},
    {"host": "", "path": "", "preerr": False, "pairs": ["foo", "{}"]},
    {"host": "", "path": "", "preerr": True, "pairs": ["foo", "bar"]},
    {"host": "", "path": "", "preerr": True, "pairs": ["foo"]},
]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k)) in enumerate(SIZES.items()):
        rng = random.Random(20190125 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append(case(rng, k))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
