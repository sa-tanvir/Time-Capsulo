"""Seeded workload generator for mux routeRegexpGroup.setMatch. Usage: python3 gen_workload.py <out_dir>"""
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

# size: (cases, variables per route)
SIZES = {"S": (4_000, 3), "M": (400, 30), "L": (40, 300)}

EDGE = [
    (R(path="/111/", strict=True), Q("http://localhost/111")),
    (R(path="/111/", strict=True), Q("http://localhost/111/")),
    (R(path="/111", strict=True), Q("http://localhost/111/")),
    (R(path="/{arg1}/{arg2:[0-9]+}/", strict=True), Q("http://localhost/foo/123")),
    (R(path="/{arg1}/{arg2:[0-9]+}", strict=True), Q("http://localhost/foo/123/?a=b#frag")),
    (R(path="/static/", prefix=True, strict=True), Q("http://localhost/static/logo.png")),
    (R(path="/v1/{v1}/v2", encoded=True), Q("http://localhost/v1/1%2F2/v2")),
    (R(path="/v1/{v1}/v2"), Q("http://localhost/v1/1%2F2/v2")),
    (R(host="{v1:[a-z]+}.google.com", path="/{v2}"), Q("http://www.google.com/x")),
    (R(host="{foo:[a-z][a-z][a-z]}.{bar:[a-z][a-z][a-z]}.{baz:[a-z][a-z][a-z]}"), Q("http://abc.def.ghi/")),
    (R(host="{foo:[a-z][a-z][a-z]}.{bar:[a-z][a-z][a-z]}.{baz:[a-z][a-z][a-z]}"), Q("http://a.b.c/")),
    (R(host="{sub}.example.com"), Q("/rel", host="news.example.com", relative=True)),
    (R(host="{v1}.domain.com", path="/{v2}/{v3}", queries=["foo", "{v4}"]), Q("http://aaa.domain.com/bbb/ccc?foo=ddd")),
    (R(queries=["foo", "{v1}", "baz", "{v2}"]), Q("http://localhost?foo=bar&baz=ding")),
    (R(queries=["foo", "{v1}"]), Q("http://localhost?foo=%25bar%26%20%2F%3D%3F")),
    (R(queries=["foo", "{v1:[0-9]+}"]), Q("http://localhost?foo=a")),
    (R(queries=["foo", "{v1}"]), Q("http://localhost")),
    (R(path="/{a}/{b}"), Q("http://localhost/x")),
    (R(), Q("http://localhost/")),
]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k)) in enumerate(SIZES.items()):
        rng = random.Random(20190125 + i)
        cases = [{"route": a, "req": b} for a, b in EDGE] if size == "S" else []
        while len(cases) < n:
            rt, rq = gen_route_and_request(rng, k, mismatch=0.05, allow_sub=False)
            cases.append({"route": rt, "req": req_out(rq)})
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
