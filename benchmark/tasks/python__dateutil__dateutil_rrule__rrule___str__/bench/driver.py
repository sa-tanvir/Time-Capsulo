"""Bench driver for dateutil.rrule.rrule.__str__. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from datetime import datetime
from dateutil import tz
from dateutil.rrule import rrule, weekday


def build(c):
    tzinfo = tz.UTC if c["aware"] else None
    kw = {"dtstart": datetime(*c["dtstart"], tzinfo=tzinfo), "interval": c["interval"]}
    for k in ("wkst", "count", "bymonth", "bymonthday", "byyearday", "byweekno", "bysetpos",
              "byhour", "byminute", "bysecond", "byeaster"):
        if k in c:
            kw[k] = c[k]
    if "until" in c:
        kw["until"] = datetime(*c["until"], tzinfo=tzinfo)
    if "byweekday" in c:
        kw["byweekday"] = [weekday(d, n) for d, n in c["byweekday"]]
    return rrule(c["freq"], **kw)


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        rules = [build(c) for c in json.load(fh)["cases"]]
    if mode == "check":
        h = hashlib.sha256()
        for r in rules:
            h.update(str(r).encode())
            h.update(b"\0")
            h.update(str(r).encode())   # second call: must be identical (no mutation)
            h.update(b"\1")
        print(json.dumps({"cases": len(rules), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for r in rules:
            acc += len(r.__str__())
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(rules), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
