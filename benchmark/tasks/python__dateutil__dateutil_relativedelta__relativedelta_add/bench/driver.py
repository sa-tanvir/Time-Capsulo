"""Bench driver for relativedelta.__add__. argv: <size> <repeat> <mode: check|time>"""
import datetime, hashlib, json, sys, time
from dateutil import tz
from dateutil.relativedelta import relativedelta, weekdays

KEYS = ["years", "months", "days", "leapdays", "hours", "minutes", "seconds", "microseconds",
        "year", "month", "day", "weekday", "hour", "minute", "second", "microsecond", "yearday"]


def mk_rd(f):
    kw = dict(zip(KEYS, f))
    wd = kw["weekday"]
    kw["weekday"] = None if wd is None else weekdays[wd[0]](wd[1])
    if kw["yearday"] is not None:
        yd = kw.pop("yearday")
        kw["yearday" if yd > 0 else "nlyearday"] = abs(yd)
    else:
        kw.pop("yearday")
    return relativedelta(**kw)


def mk_other(o):
    k = o[0]
    if k == "rd":
        return mk_rd(o[1])
    if k == "td":
        return datetime.timedelta(days=o[1], seconds=o[2], microseconds=o[3])
    if k == "date":
        return datetime.date(*o[1:4])
    if k == "dt":
        tzi = None if o[8] is None else (tz.UTC if o[8] == 0 else tz.tzoffset(None, o[8] * 60))
        return datetime.datetime(*o[1:8], tzinfo=tzi)
    if k == "int":
        return o[1]
    if k == "str":
        return o[1]
    return None


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        data = json.load(fh)
    rds = [mk_rd(f) for f in data["rds"]]
    others = [mk_other(o) for o in data["others"]]
    pairs = [(rds[a], others[b]) for a, b in data["cases"]]
    if mode == "check":
        h = hashlib.sha256()
        for r, o in pairs:
            try:
                res = r.__add__(o)
                out = "NotImplemented" if res is NotImplemented else "%s %r" % (type(res).__name__, res)
            except Exception as e:
                out = "EXC %s: %s" % (type(e).__name__, e)
            h.update(out.encode() + b"\n")
        print(json.dumps({"cases": len(pairs), "output_digest": h.hexdigest()}))
        return
    chk = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for r, o in pairs:
            res = r.__add__(o)
            chk += res is NotImplemented
    elapsed = time.perf_counter() - t0
    print(chk, file=sys.stderr)
    print(json.dumps({"cases": len(pairs), "repeat": repeat, "elapsed_s": elapsed}))


if __name__ == "__main__":
    main()
