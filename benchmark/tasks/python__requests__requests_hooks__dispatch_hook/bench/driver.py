"""Bench driver for requests.hooks.dispatch_hook. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from requests.hooks import dispatch_hook


def inc(x, **kw): return x + 1
def dbl(x, **kw): return (x * 2) % 1000003
def none(x, **kw): return None
def neg(x, **kw): return -x
def zero(x, **kw): return 0
def half(x, **kw): return x // 2
def step(x, **kw): return x + kw.get("step", 100)
def boom(x, **kw): raise ValueError("boom %d" % x)


FUNCS = {f.__name__: f for f in (inc, dbl, none, neg, zero, half, step, boom)}


def build(c):
    fs = [FUNCS[n] for n in c["chain"]]
    shape = c["shape"]
    if shape == "none":
        reg = None
    elif shape == "empty_dict":
        reg = {}
    else:
        val = fs[0] if shape == "single" else (tuple(fs) if shape == "tuple" else list(fs))
        reg = {"response": val}
        if c["extra"]:
            reg["other_event"] = [inc]
    return c["key"], reg, c["data"], c["kwargs"]


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [build(c) for c in json.load(fh)["cases"]]
    if mode == "check":
        h = hashlib.sha256()
        for key, reg, data, kw in cases:
            try:
                r = ("ok", dispatch_hook(key, reg, data, **kw))
            except ValueError as e:
                r = ("ValueError", str(e))
            h.update(repr(r).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for key, reg, data, kw in cases:
            try:
                acc += dispatch_hook(key, reg, data, **kw)
            except ValueError:
                acc += 1
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
