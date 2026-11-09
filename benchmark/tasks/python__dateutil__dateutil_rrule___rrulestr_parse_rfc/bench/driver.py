"""Bench driver for _rrulestr._parse_rfc. argv: <size> <repeat> <mode: check|time>"""
import datetime, hashlib, itertools, json, os, sys, time
from dateutil import tz
from dateutil.rrule import rrulestr, rrule

TZIDS = {"Zone/East": tz.tzoffset("EST", -18000), "Zone/West": tz.tzoffset("PST", -28800),
         "Mid-Atlantic": tz.tzoffset(None, -7200), "UTC": tz.tzutc()}
TZINFOS = {"Z": tz.tzutc(), "UTC": tz.tzutc()}
N_OCC = 15


def prepare(c):
    kw = dict(c["kw"])
    kw["tzids"] = TZIDS
    if c["ti"]:
        kw["tzinfos"] = TZINFOS
    if c["dtstart"] is not None:
        kw["dtstart"] = datetime.datetime(*c["dtstart"])
    return c["s"], kw


def describe(r):
    out = [type(r).__name__]
    if isinstance(r, rrule):
        out.append(str(r))
    else:
        out.append((len(r._rrule), len(r._rdate), len(r._exrule), len(r._exdate)))
        out.append([str(x) for x in r._rrule] + [str(x) for x in r._exrule])
    try:
        out.append(list(itertools.islice(r, N_OCC)))
    except Exception as e:
        out.append(("iter-error", type(e).__name__, str(e)))
    return repr(out)


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workload_%s.json" % size)
    with open(path) as fh:
        cases = [prepare(c) for c in json.load(fh)]
    parse = rrulestr._parse_rfc
    if mode == "check":
        h = hashlib.sha256()
        for s, kw in cases:
            try:
                rep = describe(parse(s, **kw))
            except Exception as e:
                rep = repr(("error", type(e).__name__, str(e)))
            h.update(rep.encode())
            h.update(b"\x00")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    chk = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for s, kw in cases:
            try:
                r = parse(s, **kw)
                chk += 1 if r is not None else 0
            except Exception:
                chk += 2
    el = time.perf_counter() - t0
    sys.stderr.write("checksum %d\n" % chk)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
