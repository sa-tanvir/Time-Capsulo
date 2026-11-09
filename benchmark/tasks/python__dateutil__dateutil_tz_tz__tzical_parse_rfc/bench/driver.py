"""Bench driver for tzical._parse_rfc. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from io import StringIO
from itertools import islice
from dateutil import tz

# A normal construction binds the lazily imported `rrule` module global in dateutil.tz.tz.
tz.tzical(StringIO("BEGIN:VCALENDAR\nEND:VCALENDAR\n"))


def fresh():
    obj = tz.tzical.__new__(tz.tzical)
    obj._s = "bench"
    obj._vtz = {}
    return obj


def describe(obj):
    out = []
    for key in sorted(obj._vtz):
        vtz = obj._vtz[key]
        comps = []
        for c in vtz._comps:
            occ = list(islice(c.rrule, 6)) if c.rrule is not None else None
            comps.append((c.tzoffsetfrom, c.tzoffsetto, c.isdst, c.tzname, type(c.rrule).__name__, occ))
        out.append((key, type(vtz).__name__, vtz._tzid, comps))
    return out


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for s in cases:
            obj = fresh()
            try:
                rv = obj._parse_rfc(s)
                res = ("ok", rv)
            except Exception as e:
                res = ("err", type(e).__name__, str(e))
            h.update((repr(res) + repr(describe(obj)) + "\n").encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    el, acc = 0.0, 0
    for _ in range(repeat):
        objs = [fresh() for _ in cases]
        t0 = time.perf_counter()
        for obj, s in zip(objs, cases):
            try:
                obj._parse_rfc(s)
            except ValueError:
                acc += 1
        el += time.perf_counter() - t0
        acc += sum(len(o._vtz) for o in objs)
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
