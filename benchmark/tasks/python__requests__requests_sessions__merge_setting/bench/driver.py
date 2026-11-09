"""Bench driver for merge_setting(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from collections import OrderedDict
from requests.sessions import merge_setting
from requests.structures import CaseInsensitiveDict

CLS = {"odict": OrderedDict, "cid": CaseInsensitiveDict, "dict": dict}


def val(s):
    t = s["t"]
    if t == "none":
        return None
    if t == "scalar":
        return s["v"]
    pairs = [tuple(p) for p in s["v"]]
    return OrderedDict(pairs) if t == "odict" else dict(pairs)


def decode(c):
    return val(c["req"]), val(c["ses"]), c["cls"]


def call(req, ses, cls):
    if cls == "default":
        return merge_setting(req, ses)
    return merge_setting(req, ses, dict_class=CLS[cls])


def describe(res, req, ses):
    ident = "req" if res is req else "ses" if res is ses else "new"
    if ident == "new" or isinstance(res, (dict, CaseInsensitiveDict)):
        return ident, type(res).__name__, list(res.items())
    return ident, repr(res)


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [decode(c) for c in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for req, ses, cls in cases:
            before = (repr(req), repr(ses))
            res = call(req, ses, cls)
            unchanged = before == (repr(req), repr(ses))
            h.update((repr(describe(res, req, ses)) + repr(unchanged) + "\n").encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    keep = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for req, ses, cls in cases:
            r = call(req, ses, cls)
            keep += 1 if r is None else 2
    el = time.perf_counter() - t0
    print(keep, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
