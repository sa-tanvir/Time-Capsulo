"""Bench driver for RequestEncodingMixin._encode_params(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from collections import OrderedDict
from requests.models import RequestEncodingMixin

enc = RequestEncodingMixin._encode_params


def sc(x):
    if x is None:
        return None
    if "s" in x:
        return x["s"]
    if "b" in x:
        return x["b"].encode("utf-8")
    if "i" in x:
        return x["i"]
    return x["f"]


def val(x):
    if isinstance(x, dict) and "list" in x:
        return [sc(e) for e in x["list"]]
    return sc(x)


def decode(c):
    k = c["kind"]
    if k == "raw_str":
        return c["v"]
    if k == "raw_bytes":
        return c["v"].encode("utf-8")
    if k == "none":
        return None
    if k == "int":
        return 42
    pairs = [(sc(a), val(b)) for a, b in c["v"]]
    if k == "dict":
        return OrderedDict(pairs)
    if k == "tuples":
        return tuple((a, tuple(b) if isinstance(b, list) else b) for a, b in pairs)
    return pairs


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json", encoding="utf-8") as fh:
        cases = [decode(c) for c in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for d in cases:
            try:
                out = "ok:" + repr(enc(d))
            except Exception as e:
                out = "err:" + type(e).__name__
            h.update(out.encode("utf-8") + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    keep = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for d in cases:
            r = enc(d)
            keep += 1 if r is None or isinstance(r, int) else len(r)
    el = time.perf_counter() - t0
    print(keep, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
