"""Bench driver for _ymd.resolve_ymd. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from dateutil.parser._parser import _ymd


def build(cases):
    objs = []
    for yf, df, vals in cases:
        y = _ymd()
        for v, label in vals:
            y.append(v, label)
        objs.append((y, yf, df))
    return objs


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for y, yf, df in build(cases):
            try:
                out = repr(y.resolve_ymd(yf, df))
            except Exception as e:
                out = "EXC %s: %s" % (type(e).__name__, e)
            h.update(out.encode() + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    elapsed, chk = 0.0, 0
    for _ in range(repeat):
        objs = build(cases)   # rebuilt outside the timed region
        t0 = time.perf_counter()
        for y, yf, df in objs:
            try:
                r = y.resolve_ymd(yf, df)
                chk += 1 if r[0] is None else r[0]
            except ValueError:
                chk += 7
        elapsed += time.perf_counter() - t0
    print(chk, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": elapsed}))


if __name__ == "__main__":
    main()
