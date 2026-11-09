"""Seeded workload generator for mux (*Router).Match. Usage: python3 gen_workload.py <out_dir>"""
import json, sys
from pathlib import Path

# ---- shared route/request generator (stdlib only) ----
import random
from urllib.parse import quote_plus

LOWER = "abcdefghijklmnopqrstuvwxyz"
WORDS = ["api", "v1", "users", "articles", "static", "products", "orders", "items", "docs", "img"]
PATH_PATS = [(None, lambda r: r.choice(["technology", "foo", "a-b", "x_y", "42", "hello"]) + str(r.randint(0, 99))),
             ("[0-9]+", lambda r: str(r.randint(0, 99999))),
             ("[a-z]+", lambda r: "".join(r.choice(LOWER) for _ in range(r.randint(1, 8)))),
             ("(?:asc|desc)", lambda r: r.choice(["asc", "desc"])),
             (r"\d{4}-\d{2}", lambda r: "%04d-%02d" % (r.randint(1990, 2030), r.randint(1, 12)))]
HOST_PATS = [(None, lambda r: r.choice(["www", "news", "api-2", "eu"])),
             ("[a-z]+", lambda r: "".join(r.choice(LOWER) for _ in range(r.randint(1, 6))))]
HEADER_KEYS = ["Content-Type", "X-Requested-With", "Accept", "X-Api-Key", "X-Trace-Id"]

def tok(name, pat):
    return "{%s}" % name if pat is None else "{%s:%s}" % (name, pat)

def gen_route_and_request(rng, k, mismatch=0.15, allow_sub=True):
    """Returns (route_spec, request_spec). k = scale (number of variables / matchers)."""
    rt = {"host": "", "path": "", "prefix": False, "strict": rng.random() < 0.2, "encoded": rng.random() < 0.15,
          "methods": [], "schemes": [], "headers": [], "headersRe": [], "queries": [], "sub": [], "buildOnly": False}
    rq = {"method": "GET", "scheme": "http", "host": "example.com", "path": "/", "query": [], "headers": [],
          "relative": rng.random() < 0.2}
    nh = rng.choice([0, 1, 2]) if rng.random() < 0.5 else 0
    nq = rng.randint(0, max(1, k // 4))
    npv = max(1, k - nh - nq)
    if nh or rng.random() < 0.2:
        parts, hv = [], []
        for i in range(nh):
            pat, good = rng.choice(HOST_PATS)
            parts.append(tok("h%d" % i, pat)); hv.append(good(rng))
        rt["host"] = ".".join(parts + ["example", "com"])
        rq["host"] = ".".join(hv + ["example", "com"])
    segs, vsegs = [], []
    for i in range(npv):
        if rng.random() < 0.4:
            w = rng.choice(WORDS); segs.append(w); vsegs.append(w)
        pat, good = rng.choice(PATH_PATS)
        v = good(rng)
        if rt["encoded"] and pat is None and rng.random() < 0.3:
            v = v + "%2F" + v                                   # encoded slash inside one segment
        segs.append(tok("p%d" % i, pat)); vsegs.append(v)
    rt["path"] = "/" + "/".join(segs)
    rq["path"] = "/" + "/".join(vsegs)
    base_tpl, base_path = rt["path"], rq["path"]
    r = rng.random()
    if r < 0.15:
        rt["prefix"] = True
        rq["path"] += "/" + "/".join(rng.choice(WORDS) for _ in range(rng.randint(1, 3)))
    elif rt["strict"] and r < 0.6:
        if rng.random() < 0.5:
            rt["path"] += "/"
        if rng.random() < 0.5:
            rq["path"] += "/"
    elif r < 0.3:
        rt["path"] += "/"; rq["path"] += "/"
    for i in range(nq):
        key = "k%d" % i
        if rng.random() < 0.7:
            pat = rng.choice([None, "[0-9]+", "[a-z]+"])
            rt["queries"] += [key, tok("q%d" % i, pat)]
            val = str(rng.randint(0, 9999)) if pat == "[0-9]+" else "".join(rng.choice(LOWER) for _ in range(rng.randint(1, 6))) if pat else rng.choice(["x", "a b", "1&2", "", "z=z"])
        else:
            val = rng.choice(["bar", "ding", "1"])
            rt["queries"] += [key, rng.choice([val, ""])]
        rq["query"].append([key, val])
    for i in range(rng.randint(0, 3)):
        rq["query"].append(["extra%d" % i, str(i)])
    rng.shuffle(rq["query"])
    if rng.random() < 0.4:
        rt["methods"] = rng.sample(["GET", "POST", "PUT", "delete", "PATCH"], rng.randint(1, 3))
        rq["method"] = rng.choice(rt["methods"]).upper()
    if rng.random() < 0.2:
        rt["schemes"] = rng.sample(["http", "HTTPS"], rng.randint(1, 2))
        rq["scheme"] = rng.choice(rt["schemes"]).lower()
    for i in range(rng.randint(0, 2)):
        hk = rng.choice(HEADER_KEYS)
        hv = rng.choice(["application/json", "XMLHttpRequest", "text/html", "abc"])
        rt["headers"] += [hk.lower() if rng.random() < 0.5 else hk, rng.choice([hv, ""])]
        rq["headers"] += [hk, hv]
    if rng.random() < 0.2:
        rt["headersRe"] = ["Accept", "(?:html|json)"]
        rq["headers"] += ["Accept", rng.choice(["text/html", "application/json", "application/xhtml+xml"])]
    if rq["relative"] and rt["schemes"]:
        rq["relative"] = False
    if allow_sub and rng.random() < 0.15:
        # subrouter below a path prefix: child route path is relative to the parent prefix
        rt["prefix"] = True
        rt["strict"] = False
        child_seg = rng.choice(WORDS)
        rt["path"], rq["path"] = base_tpl, base_path
        child = {"host": "", "path": "/" + child_seg + "/{c0}", "prefix": False, "strict": False, "encoded": False,
                 "methods": [], "schemes": [], "headers": [], "headersRe": [], "queries": [], "sub": [], "buildOnly": False}
        rt["sub"] = [child]
        rq["path"] = rq["path"].rstrip("/") + "/" + child_seg + "/" + "c" + str(rng.randint(0, 99))
    if rng.random() < mismatch:
        what = rng.choice(["method", "path", "host", "query", "header", "scheme", "buildOnly"])
        if what == "method":
            rq["method"] = "OPTIONS"
        elif what == "path":
            rq["path"] = "/nomatch" + rq["path"]
        elif what == "host":
            rq["host"] = "other.org"
        elif what == "query" and rq["query"]:
            rq["query"] = rq["query"][1:]
        elif what == "header" and rq["headers"]:
            rq["headers"] = rq["headers"][2:]
        elif what == "scheme":
            rq["scheme"] = "ftp"
        elif what == "buildOnly":
            rt["buildOnly"] = True
    return rt, rq

def request_url(rq):
    q = "&".join(quote_plus(a) + "=" + quote_plus(b) for a, b in rq["query"])
    u = rq["path"] + ("?" + q if q else "")
    if rq["relative"]:
        return u
    return rq["scheme"] + "://" + rq["host"] + u

def req_out(rq):
    return {"method": rq["method"], "url": request_url(rq), "host": rq["host"], "relative": rq["relative"],
            "headers": rq["headers"]}

def R(**kw):
    d = {"host": "", "path": "", "prefix": False, "strict": False, "encoded": False, "methods": [], "schemes": [],
         "headers": [], "headersRe": [], "queries": [], "sub": [], "buildOnly": False}
    d.update(kw)
    return d

def Q(url, method="GET", headers=(), host="", relative=False):
    return {"method": method, "url": url, "host": host, "relative": relative, "headers": list(headers)}
# ---- end shared ----

# size: (routers, routes per router, requests per router)
SIZES = {"S": (300, 4, 20), "M": (30, 40, 20), "L": (4, 400, 40)}

def router(rng, nroutes, nreq):
    routes, reqs = [], []
    for j in range(nroutes):
        rt, rq = gen_route_and_request(rng, 3, mismatch=0.0, allow_sub=True)
        if rt["sub"]:
            rt["subMw"] = rng.choice([0, 0, 1, 2])
            rt["subNF"] = rng.random() < 0.3
            rt["subMNA"] = rng.random() < 0.2
        routes.append(rt); reqs.append(rq)
    out = []
    for _ in range(nreq):
        j = rng.randrange(nroutes)
        rq = json.loads(json.dumps(reqs[j]))
        r = rng.random()
        if r < 0.15:
            rq["path"] = "/nomatch" + rq["path"]                       # 404
        elif r < 0.3:
            rq["method"] = "OPTIONS"                                   # 405 if the route has methods
        elif r < 0.35 and routes[j]["sub"]:
            rq["path"] = rq["path"].rsplit("/", 2)[0] + "/zz/1"        # subrouter-level 404
        out.append(req_out(rq))
    return {"routes": routes, "mw": rng.choice([0, 0, 1, 2, 3]), "nf": rng.random() < 0.3, "mna": rng.random() < 0.3,
            "reqs": out}

def RT(routes, reqs, mw=0, nf=False, mna=False):
    return {"routes": routes, "mw": mw, "nf": nf, "mna": mna, "reqs": reqs}

EDGE = [
    RT([R(path="/products/")], [Q("http://www.example.com/products/"), Q("http://www.example.com/products")]),
    RT([R(host="www.example.com", sub=[R(path="/products/")])], [Q("http://www.example.com/products/"), Q("http://other.com/products/")]),
    RT([R(path="/", methods=["GET", "POST"])], [Q("http://localhost/", method="PUT"), Q("http://localhost/", method="GET")]),
    RT([R(path="/", methods=["GET", "POST"]), R(path="/", methods=["PUT"])], [Q("http://localhost/", method="PUT"), Q("http://localhost/", method="DELETE")], mw=2),
    RT([R(path="/", methods=["GET"])], [Q("http://localhost/", method="POST"), Q("http://localhost/x")], mna=True, nf=True, mw=1),
    RT([R(path="/"), R(path="/sub/", prefix=True, sub=[R(path="/")])], [Q("/sub/whatever", relative=True, host="localhost"), Q("http://localhost/sub/")]),
    RT([R(path="/"), dict(R(path="/sub/", prefix=True, sub=[R(path="/")]), subNF=True)], [Q("/sub/whatever", relative=True, host="localhost")], mw=1),
    RT([R(path="/"), dict(R(path="/sub/", prefix=True, sub=[R(path="/")]), subNF=True)], [Q("/sub/whatever", relative=True, host="localhost")], nf=True),
    RT([dict(R(path="/sub", prefix=True, sub=[R(path="/x", methods=["GET"])]), subMw=1)], [Q("http://localhost/sub/x"), Q("http://localhost/sub/x", method="POST"), Q("http://localhost/sub/y")], mw=1),
    RT([dict(R(path="/sub", prefix=True, sub=[R(path="/x", methods=["GET"])]), subMNA=True)], [Q("http://localhost/sub/x", method="POST")], mw=1),
    RT([R(headers=["SomeSpecialHeader", ""], sub=[R(path="/")]), R(path="/")], [Q("http://localhost/", headers=["SomeSpecialHeader", "foo"]), Q("http://localhost/")]),
    RT([R(path="/111/", strict=True)], [Q("http://localhost/111")], mw=2),
    RT([], [Q("http://localhost/")]),
    RT([], [Q("http://localhost/")], nf=True, mw=1),
]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, nroutes, nreq)) in enumerate(SIZES.items()):
        rng = random.Random(20190125 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append(router(rng, nroutes, nreq))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
