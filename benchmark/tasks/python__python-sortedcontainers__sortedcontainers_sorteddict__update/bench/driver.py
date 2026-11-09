"""Bench driver for SortedDict.update. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, random, sys, time
from operator import neg
from sortedcontainers import SortedDict


def mk_key(i, str_keys):
    return "k%07d" % i if str_keys else i


def expand(c):
    """Return (base_items, args, kwargs, key_fn) for a case recipe."""
    rng = random.Random(c["seed"])
    sk, ks = c["str_keys"], c["keyspace"]
    base = [(mk_key(rng.randrange(ks), sk), rng.randrange(1000)) for _ in range(c["n_base"])]
    upd = [(mk_key(rng.randrange(ks), sk), rng.randrange(1000)) for _ in range(c["n_upd"])]
    form = c["form"]
    if form == "dict":
        args, kw = (dict(upd),), {}
    elif form == "pairs":
        args, kw = (upd,), {}
    elif form == "kwargs":
        args, kw = (), dict(upd)
    elif form == "mixed":
        half = len(upd) // 2
        args, kw = (upd[:half],), dict(upd[half:])
    elif form == "sorteddict":
        sd = SortedDict()
        dict.update(sd, upd)
        sd._list.update(dict.keys(sd))
        args, kw = (sd,), {}
    else:  # none: empty call
        args, kw = (), {}
    return base, args, kw, (neg if c["key_fn"] == "neg" else None)


def build(base, key_fn):
    """Build the receiver without calling update (SortedDict() with no args only hits the empty path)."""
    sd = SortedDict(key_fn) if key_fn else SortedDict()
    dict.update(sd, base)
    sd._list.update(dict.keys(sd))
    return sd


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        recipes = json.load(fh)
    cases = [expand(c) for c in recipes]
    if mode == "check":
        h = hashlib.sha256()
        for base, args, kw, key_fn in cases:
            sd = build(base, key_fn)
            try:
                r = sd.update(*args, **kw)
                out = repr((r, list(sd.items()), len(sd._list), dict.__len__(sd)))
            except Exception as e:  # noqa
                out = "ERR " + type(e).__name__
            h.update(out.encode() + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc, el = 0, 0.0
    for _ in range(repeat):
        for base, args, kw, key_fn in cases:
            sd = build(base, key_fn)
            t0 = time.perf_counter()
            sd.update(*args, **kw)
            el += time.perf_counter() - t0
            acc += len(sd)
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
