"""Bench driver for Request.__init__. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from requests.models import Request


def mk(i):
    def hook(r, **kw):
        return r
    hook.idx = i
    return hook


FUNCS = [mk(i) for i in range(8)]
NOT_CALLABLE = "not-a-hook"


def build(c):
    p = c["present"]
    kw = {}
    vals = {"method": "POST", "url": b"http://example.com/" if c["falsy"] else "http://example.com/a",
            "headers": {} if c["falsy"] else {"X-A": "1"}, "files": {"f": b"abc"}, "data": "" if c["falsy"] else {"k": "v"},
            "params": [("a", "1")], "auth": ("u", "p"), "cookies": {"c": "1"}, "json": {"j": [1, 2]}}
    for k, v in vals.items():
        if p[k]:
            kw[k] = v
    h = c["hooks"]
    if h is not None:
        if h["kind"] == "bad":
            kw["hooks"] = {"response": [FUNCS[0]], "request": FUNCS[1]}
        elif h["kind"] == "single":
            kw["hooks"] = {"response": FUNCS[h["fn"]]}
        else:
            items = [FUNCS[i] if i >= 0 else NOT_CALLABLE for i in h["items"]]
            kw["hooks"] = {"response": items if h["kind"] == "list" else tuple(items)}
    return kw


def describe(r, kw):
    out = []
    for a in ["method", "url", "headers", "files", "data", "params", "auth", "cookies", "json"]:
        v = getattr(r, a)
        out.append((a, repr(v), a in kw and v is kw[a]))
    hooks = {k: [getattr(f, "idx", repr(f)) for f in v] for k, v in r.hooks.items()}
    shared = "hooks" in kw and (r.hooks is kw["hooks"] or any(
        r.hooks.get(k) is v for k, v in kw["hooks"].items()))
    return out, sorted(hooks.items()), shared, sorted(vars(r).keys())


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [build(c) for c in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for kw in cases:
            try:
                out = "ok:" + repr(describe(Request(**kw), kw))
            except Exception as e:
                out = "err:" + type(e).__name__ + ":" + repr(e.args)
            h.update(out.encode() + b"\n")
        # defaults must be fresh containers per instance
        a, b = Request(), Request()
        h.update(repr((a.headers is b.headers, a.data is b.data, a.hooks is b.hooks)).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    keep = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for kw in cases:
            try:
                keep += len(Request(**kw).hooks["response"])
            except ValueError:
                keep += 1
    el = time.perf_counter() - t0
    print(keep, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
