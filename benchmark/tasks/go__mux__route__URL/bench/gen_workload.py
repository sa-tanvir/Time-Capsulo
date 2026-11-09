"""Seeded workload generator for mux Route.URL. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# size: (cases, route variables per route)
SIZES = {"S": (5_000, 3), "M": (500, 30), "L": (50, 300)}
WORDS = ["api", "v1", "users", "articles", "static", "products", "orders", "items"]
PATS = [(None, lambda r: r.choice(["technology", "foo", "a-b", "42", "hello world", "x%2Fy"]), "a/b"),
        ("[0-9]+", lambda r: str(r.randint(0, 99999)), "12a"),
        ("[a-z]+", lambda r: "".join(r.choice("abcdefgh") for _ in range(r.randint(1, 6))), "Abc"),
        ("(?:asc|desc)", lambda r: r.choice(["asc", "desc"]), "up")]

def var(rng, name, vals):
    pat, good, bad = rng.choice(PATS)
    v = bad if rng.random() < BAD[0] else good(rng)
    vals += [name, v]
    return "{%s}" % name if pat is None else "{%s:%s}" % (name, pat)

BAD = [0.01]

def case(rng, k):
    BAD[0] = 0.04 / k                                           # ~4% of cases carry one invalid value
    vals = []
    nh = rng.choice([0, 0, 1, 2]) if k > 3 else rng.choice([0, 1])
    nq = rng.randint(0, max(1, k // 3))
    npth = max(0, k - nh - nq)
    host = ""
    if rng.random() < 0.6:
        host = ".".join([var(rng, "h%d" % i, vals) for i in range(nh)] + ["example", "com"])
    path = ""
    if rng.random() < 0.9:
        segs = []
        for i in range(npth):
            if rng.random() < 0.4:
                segs.append(rng.choice(WORDS))
            segs.append(var(rng, "p%d" % i, vals))
        path = "/" + "/".join(segs) if segs else "/" + rng.choice(WORDS)
        if rng.random() < 0.2:
            path += "/"
    queries = []
    for i in range(nq):
        r = rng.random()
        queries += ["k%d" % i, var(rng, "q%d" % i, vals) if r < 0.7 else rng.choice(["", "lit", "a b"])]
    schemes = rng.choice([[], [], ["https"], ["HTTPS", "http"], ["ftp"]])
    pairs = []
    order = list(range(0, len(vals), 2)); rng.shuffle(order)
    for j in order:
        pairs += vals[j:j + 2]
    r = rng.random()
    if r < 0.03 and pairs:
        del pairs[0:2]                                          # missing variable
    elif r < 0.05:
        pairs.append("odd")                                     # odd number of strings
    elif r < 0.25:
        pairs += ["unused", "x"]
    return {"host": host, "path": path, "prefix": rng.random() < 0.1, "queries": queries, "schemes": schemes,
            "bvf": rng.random() < 0.2, "preerr": rng.random() < 0.01, "pairs": pairs}

def mk(host="", path="", queries=(), schemes=(), pairs=(), prefix=False, bvf=False, preerr=False):
    return {"host": host, "path": path, "prefix": prefix, "queries": list(queries), "schemes": list(schemes),
            "bvf": bvf, "preerr": preerr, "pairs": list(pairs)}

EDGE = [
    mk(host="foo.domain.com"),
    mk(host="{subdomain}.domain.com", pairs=["subdomain", "bar"]),
    mk(host="foo.domain.com", path="/articles"),
    mk(path="/articles"),
    mk(path="/articles/{category}/{id:[0-9]+}", pairs=["category", "technology", "id", "42"]),
    mk(host="{subdomain}.domain.com", path="/articles/{category}/{id:[0-9]+}", pairs=["subdomain", "foo", "category", "technology", "id", "42"]),
    mk(host="{subdomain}.domain.com", path="/articles/{category}/{id:[0-9]+}", pairs=["subdomain", "foo", "category", "technology", "id", "x"]),
    mk(host="{subdomain}.domain.com", path="/articles/{category}", pairs=["category", "technology"]),
    mk(host="localhost"), mk(host="localhost", schemes=["https", "ftp"]), mk(host="localhost", schemes=["ftp", "https"]),
    mk(path="/a", schemes=["https"]),
    mk(host="www.example.com", path="/api", queries=["foo", "bar", "baz", "ding"]),
    mk(queries=["foo", "{v1}"], pairs=["v1", "%bar& /=?"]),
    mk(queries=["foo", "{v1:[0-9]+}"], pairs=["v1", "x"]),
    mk(queries=["foo", ""]),
    mk(path="/a/{x}", pairs=["x"]),
    mk(path="/static/", prefix=True),
    mk(path="/a/{x}", bvf=True, pairs=["x", "1"]),
    mk(path="/a/{x}", preerr=True, pairs=["x", "1"]),
    mk(),
]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k)) in enumerate(SIZES.items()):
        rng = random.Random(20190125 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append(case(rng, k))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
