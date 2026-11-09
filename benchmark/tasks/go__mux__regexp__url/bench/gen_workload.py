"""Seeded workload generator for mux routeRegexp.url. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# size: (cases, variables per template)
SIZES = {"S": (6_000, 2), "M": (600, 20), "L": (60, 200)}
PATH, HOST, PREFIX, QUERY = 0, 1, 2, 3
WORDS = ["api", "v1", "users", "articles", "static", "img", "products", "orders", "items", "docs"]
# (pattern or None for default, valid value generator, invalid value)
PATS = [
    (None, lambda r: r.choice(["technology", "foo", "a-b", "x_y", "42", "hello world", "a&b", "100%"]), "a/b"),
    ("[0-9]+", lambda r: str(r.randint(0, 99999)), "12a"),
    ("[a-z]+", lambda r: "".join(r.choice("abcdefghij") for _ in range(r.randint(1, 8))), "Abc"),
    ("[a-z]{2}", lambda r: r.choice(["en", "fr", "de"]), "eng"),
    ("(?:foo|bar)", lambda r: r.choice(["foo", "bar"]), "baz"),
    (r"\d{4}-\d{2}", lambda r: "%04d-%02d" % (r.randint(1990, 2030), r.randint(1, 12)), "2019-1"),
    (".*", lambda r: r.choice(["", "x/y/z", "any thing", "a=b&c"]), None),
]
HOSTPATS = [
    (None, lambda r: r.choice(["www", "news", "api-2", "eu"]), "a.b"),
    ("[a-z]+", lambda r: "".join(r.choice("abcdefghij") for _ in range(r.randint(1, 8))), "a1"),
]

def build(rng, typ, k, pats):
    parts, vals, names = [], [], []
    for i in range(k):
        name = rng.choice(["id", "name", "cat", "v", "x-y", "slug"]) + str(i)
        pat, good, bad = rng.choice(pats)
        names.append(name)
        token = "{%s}" % name if pat is None else "{%s:%s}" % (name, pat)
        parts.append(token)
        v = good(rng)
        if bad is not None and rng.random() < 0.02:
            v = bad
        vals.append([name, v])
    if typ == HOST:
        lits = [rng.choice(["", "sub", "x"]) for _ in parts]
        tpl = ".".join(l + p for l, p in zip(lits, parts)) + ".example.com"
    elif typ == QUERY:
        tpl = rng.choice(["q", "foo", "id"]) + "=" + "-".join(parts)
    else:
        segs = []
        for p in parts:
            if rng.random() < 0.5:
                segs.append(rng.choice(WORDS))
            segs.append(p)
        tpl = "/" + "/".join(segs)
        if rng.random() < 0.3:
            tpl += "/"
    r = rng.random()
    if r < 0.05 and vals:
        vals.pop(rng.randrange(len(vals)))                      # missing variable
    if rng.random() < 0.3:
        vals.append(["unused", "extra"])                        # extra keys are ignored
    rng.shuffle(vals)
    return tpl, vals

def case(rng, k):
    typ = rng.choice([PATH, PATH, HOST, PREFIX, QUERY])
    tpl, vals = build(rng, typ, k, HOSTPATS if typ == HOST else PATS)
    return {"tpl": tpl, "typ": typ, "strict": rng.random() < 0.3, "vals": vals}

EDGE = [
    {"tpl": "/articles/{category}/{id:[0-9]+}", "typ": PATH, "strict": False, "vals": [["category", "technology"], ["id", "42"]]},
    {"tpl": "/articles/{category}/{id:[0-9]+}", "typ": PATH, "strict": False, "vals": [["category", "technology"], ["id", "x"]]},
    {"tpl": "/articles/{category}/{id:[0-9]+}", "typ": PATH, "strict": False, "vals": [["category", "technology"]]},
    {"tpl": "{subdomain}.domain.com", "typ": HOST, "strict": False, "vals": [["subdomain", "foo"]]},
    {"tpl": "{v1:[a-z]+}.google.com", "typ": HOST, "strict": False, "vals": [["v1", "Bad"]]},
    {"tpl": "/111/", "typ": PATH, "strict": True, "vals": []},
    {"tpl": "/{v1}/", "typ": PATH, "strict": True, "vals": [["v1", "x"]]},
    {"tpl": "/static/", "typ": PREFIX, "strict": True, "vals": []},
    {"tpl": "/v1/{v1}/v2", "typ": PATH, "strict": False, "vals": [["v1", "1%2F2"]]},
    {"tpl": "/a/{v1}", "typ": PATH, "strict": False, "vals": [["v1", "x/y"]]},
    {"tpl": "/111/{v1:\\d}{v2:.*}", "typ": PATH, "strict": False, "vals": [["v1", "3"], ["v2", "a"]]},
    {"tpl": "foo=bar", "typ": QUERY, "strict": False, "vals": []},
    {"tpl": "foo=", "typ": QUERY, "strict": False, "vals": []},
    {"tpl": "foo={v1}", "typ": QUERY, "strict": False, "vals": [["v1", "%bar& /=?"]]},
    {"tpl": "foo={v1:[0-9]+}", "typ": QUERY, "strict": False, "vals": [["v1", "10"]]},
    {"tpl": "foo={v1:[0-9]+}", "typ": QUERY, "strict": False, "vals": [["v1", "1 0"]]},
    {"tpl": "foo={v1:[a-z ]+}", "typ": QUERY, "strict": False, "vals": [["v1", "a b"]]},
    {"tpl": "foo={v1:[0-9]{1}(?:a|b)}", "typ": QUERY, "strict": False, "vals": [["v1", "1a"]]},
    {"tpl": "/{a}/{b}", "typ": PATH, "strict": False, "vals": [["a", "x"], ["b", "y/z"], ["c", "w"]]},
    {"tpl": "/{a:[0-9]+}/{b:[0-9]+}", "typ": PATH, "strict": False, "vals": [["a", "x"], ["b", "y"]]},
    {"tpl": "", "typ": PATH, "strict": False, "vals": []},
]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k)) in enumerate(SIZES.items()):
        rng = random.Random(20190125 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append(case(rng, k))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
