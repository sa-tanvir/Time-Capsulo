"""Seeded workload generator for mux routeRegexp.getURLQuery. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path
from urllib.parse import quote_plus

# size: (cases, query parameters per request URL)
SIZES = {"S": (10_000, 3), "M": (1_000, 30), "L": (100, 300)}
KEYS = ["foo", "bar", "baz", "id", "page", "q", "sort", "lang", "filter", "token", "a", "b"]
TEMPLATES = [("foo={v1}", 3), ("foo=bar", 3), ("foo=", 3), ("id={id:[0-9]+}", 3), ("q={q}", 3),
             ("page={p:[0-9]+}", 3), ("filter=", 3), ("missing={m}", 3), ("/path/{v}", 0), ("{h}.example.com", 1)]

def rval(rng):
    r = rng.random()
    if r < 0.4:
        return str(rng.randint(0, 10**6))
    if r < 0.8:
        return "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(0, 12)))
    return "".join(rng.choice("abc %&/=?+é") for _ in range(rng.randint(1, 8)))

def case(rng, k):
    tpl, typ = rng.choice(TEMPLATES)
    params = []
    for i in range(k):
        key = rng.choice(KEYS) + (str(i) if rng.random() < 0.7 else "")
        params.append((key, rval(rng)))
    tkey = tpl.split("=")[0]
    r = rng.random()
    if r < 0.6 and typ == 3:
        params.insert(rng.randrange(len(params) + 1), (tkey, rval(rng)))
    if r < 0.15 and typ == 3:
        params.insert(rng.randrange(len(params) + 1), (tkey, rval(rng)))      # duplicate key: first wins
    q = "&".join(quote_plus(a) + "=" + quote_plus(b) if rng.random() < 0.95 else quote_plus(a) for a, b in params)
    return {"tpl": tpl, "typ": typ, "q": q}

EDGE = [
    {"tpl": "foo=bar", "typ": 3, "q": "foo=bar&baz=ding"},
    {"tpl": "baz=ding", "typ": 3, "q": "foo=bar&baz=dong"},
    {"tpl": "foo={v1}", "typ": 3, "q": "bar=2&foo=1"},
    {"tpl": "foo=", "typ": 3, "q": ""},
    {"tpl": "foo=", "typ": 3, "q": "foo="},
    {"tpl": "foo=", "typ": 3, "q": "foo"},
    {"tpl": "foo=bar", "typ": 3, "q": "fffoo=bar&baz=dingggg"},
    {"tpl": "foo={v1}", "typ": 3, "q": "foo=%25bar%26%20%2F%3D%3F"},
    {"tpl": "foo={v1}", "typ": 3, "q": "foo=a&foo=b"},
    {"tpl": "foo={v1}", "typ": 3, "q": "foo=a+b"},
    {"tpl": "f%20o={v1}", "typ": 3, "q": "f+o=1"},
    {"tpl": "f o={v1}", "typ": 3, "q": "f+o=1"},
    {"tpl": "/foo", "typ": 0, "q": "foo=bar"},
    {"tpl": "foo.com", "typ": 1, "q": "foo=bar"},
    {"tpl": "/foo", "typ": 2, "q": "foo=bar"},
]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k)) in enumerate(SIZES.items()):
        rng = random.Random(20190125 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append(case(rng, k))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
