"""Bench driver for rruleset._iter. argv: <size> <repeat> <mode: check|time>"""
import datetime, hashlib, json, os, sys, time
from dateutil.rrule import rrule, rruleset, HOURLY, DAILY, WEEKLY

BASE = datetime.datetime(2000, 1, 1)
FREQ = {"HOURLY": HOURLY, "DAILY": DAILY, "WEEKLY": WEEKLY}


def at(h):
    return BASE + datetime.timedelta(hours=h)


def mk_rule(r):
    return rrule(FREQ[r["freq"]], dtstart=at(r["start"]), interval=r["interval"],
                 count=r["count"], byhour=r["byhour"])


def build(c):
    """Construct a fresh, uncached rruleset (outside any timed region)."""
    rs = rruleset(cache=False)
    for r in c["rrules"]:
        rs.rrule(mk_rule(r))
    for h in c["rdates"]:
        rs.rdate(at(h))
    for r in c["exrules"]:
        rs.exrule(mk_rule(r))
    for h in c["exdates"]:
        rs.exdate(at(h))
    return rs


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workload_%s.json" % size)
    with open(path) as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for c in cases:
            rs = build(c)
            try:
                out = list(rs._iter())
                rep = repr((out, rs._len))
            except Exception as e:
                rep = repr(("error", type(e).__name__, str(e)))
            h.update(rep.encode())
            h.update(b"\x00")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    chk = 0
    elapsed = 0.0
    for _ in range(repeat):
        sets = [build(c) for c in cases]   # rebuilt each round: _iter sorts the date lists in place
        t0 = time.perf_counter()
        for rs in sets:
            chk += len(list(rs._iter()))
        elapsed += time.perf_counter() - t0
    sys.stderr.write("checksum %d\n" % chk)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": elapsed}))


if __name__ == "__main__":
    main()
