"""Bench driver for _rrulestr._parse_date_value. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, os, sys, time
from dateutil import tz
from dateutil.rrule import rrulestr

TZMAP = {"Zone/East": tz.tzoffset("EST", -18000), "Zone/West": tz.tzoffset("PST", -28800),
         "Mid-Atlantic": tz.tzoffset(None, -7200), "UTC": tz.tzutc()}
TZINFOS = {"Z": tz.tzutc(), "UTC": tz.tzutc(), "XYZ": 5400}


class LookupFailure(Exception):
    pass


def tz_callable(name):
    return TZMAP.get(name, tz.tzoffset(name, 3600))


def tz_raising(name):
    raise LookupFailure("no zone for " + name)


TZIDS = {"map": TZMAP, "call": tz_callable, "none": None, "bad": 42, "raise": tz_raising}


def prepare(c):
    return (c["value"], c["parms"], c["rule_tzids"], c["ignoretz"], TZIDS[c["tzids"]],
            TZINFOS if c["ti"] else None)


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workload_%s.json" % size)
    with open(path) as fh:
        cases = [prepare(c) for c in json.load(fh)]
    fn = rrulestr._parse_date_value
    if mode == "check":
        h = hashlib.sha256()
        for args in cases:
            try:
                rep = repr(fn(*args))
            except Exception as e:
                rep = repr(("error", type(e).__name__, str(e)))
            h.update(rep.encode())
            h.update(b"\x00")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    chk = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for args in cases:
            try:
                chk += len(fn(*args))
            except Exception:
                chk += 1
    el = time.perf_counter() - t0
    sys.stderr.write("checksum %d\n" % chk)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
