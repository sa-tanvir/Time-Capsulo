"""Bench driver for isoparser._parse_isotime. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from dateutil.parser.isoparser import isoparser


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [s.encode("ascii") for s in json.load(fh)]
    p = isoparser()
    if mode == "check":
        h = hashlib.sha256()
        for s in cases:
            try:
                out = repr(p._parse_isotime(s))
            except Exception as e:
                out = "EXC %s: %s" % (type(e).__name__, e)
            h.update(s + b" -> " + out.encode() + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    fn = p._parse_isotime
    chk = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for s in cases:
            try:
                chk += fn(s)[3]
            except ValueError:
                chk += 1
    elapsed = time.perf_counter() - t0
    print(chk, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": elapsed}))


if __name__ == "__main__":
    main()
