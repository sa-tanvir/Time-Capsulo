"""Bench driver for parser._parse. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from dateutil.parser._parser import parser, parserinfo


def make_parser():
    info = parserinfo()
    info._year, info._century = 2019, 2000     # pin two-digit-year window (no host-clock dependence)
    return parser(info)


def canon(out):
    res, skipped = out
    if res is None:
        return repr((None, skipped))
    return repr((repr(res), getattr(res, "century_specified", None), skipped))


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [(s, kw) for s, kw in json.load(fh)]
    p = make_parser()
    if mode == "check":
        h = hashlib.sha256()
        for s, kw in cases:
            try:
                r = canon(p._parse(s, **kw))
            except Exception as e:
                r = "EXC %s: %s" % (type(e).__name__, e)
            h.update(r.encode()); h.update(b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    f = p._parse
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for s, kw in cases:
            res, _sk = f(s, **kw)
            acc += res is None
    el = time.perf_counter() - t0
    print("checksum", acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
