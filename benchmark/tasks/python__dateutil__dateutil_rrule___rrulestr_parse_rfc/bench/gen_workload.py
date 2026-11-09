"""Seeded workload generator for _rrulestr._parse_rfc. Usage: python3 gen_workload.py <out_dir>

Each case: {"s": rule text, "kw": keyword flags, "dtstart": [y,m,d,h,mi,s] or null,
"ti": pass the driver's tzinfos mapping}. TZID names are resolved by the driver through a
fixed tzids mapping of tzoffset objects (no system tz lookups). Per-case line count grows ~10x.
"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (60, 10), "M": (50, 100), "L": (50, 1000)}   # (cases, max date entries per case)
TZNAMES = ["Zone/East", "Zone/West", "Mid-Atlantic", "UTC"]
FREQS = ["YEARLY", "MONTHLY", "WEEKLY", "DAILY", "HOURLY", "MINUTELY", "SECONDLY"]
WD = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def dtstr(rng, date_only=False):
    y, m, d = rng.randint(1990, 2030), rng.randint(1, 12), rng.randint(1, 28)
    if date_only:
        return "%04d%02d%02d" % (y, m, d)
    return "%04d%02d%02dT%02d%02d%02d" % (y, m, d, rng.randint(0, 23), rng.choice([0, 0, 15, 30, 45]),
                                          rng.choice([0, 0, 0, 30]))


def rule(rng, aware, low=False):
    freq = rng.choice(FREQS[:4] * 3 + FREQS[4:])
    parts = ["FREQ=" + freq]
    if rng.random() < 0.4:
        parts.append("INTERVAL=%d" % rng.randint(1, 4))
    if rng.random() < 0.7:
        parts.append("COUNT=%d" % rng.randint(1, 30))
    else:
        parts.append("UNTIL=" + dtstr(rng) + ("Z" if aware else ""))
    if freq in ("YEARLY", "MONTHLY", "WEEKLY", "DAILY"):
        if rng.random() < 0.6:
            days = rng.sample(WD, rng.randint(1, 3))
            if freq in ("YEARLY", "MONTHLY"):
                days = [rng.choice([d, "+1" + d, "-1" + d, "2" + d, d + "(+2)", d + "(-1)"]) for d in days]
            key = rng.choice(["BYDAY", "BYDAY", "BYWEEKDAY"])
            parts.append(key + "=" + ",".join(days))
        if freq in ("YEARLY", "MONTHLY") and rng.random() < 0.4:
            parts.append("BYMONTHDAY=" + ",".join(str(x) for x in rng.sample(range(1, 29), rng.randint(1, 3))))
        if freq == "YEARLY" and rng.random() < 0.4:
            parts.append("BYMONTH=" + ",".join(str(x) for x in rng.sample(range(1, 13), rng.randint(1, 4))))
        if rng.random() < 0.3:
            parts.append("BYHOUR=" + ",".join(str(x) for x in sorted(rng.sample(range(24), rng.randint(1, 3)))))
        if rng.random() < 0.2:
            parts.append("BYMINUTE=" + ",".join(str(x) for x in rng.sample([0, 15, 30, 45], 2)))
        if rng.random() < 0.15:
            parts.append("BYSECOND=0")
        if freq == "MONTHLY" and rng.random() < 0.2 and not any(p.startswith("BYMONTHDAY") for p in parts):
            parts.append("BYDAY=MO,TU,WE,TH,FR")
            parts.append("BYSETPOS=" + rng.choice(["1", "-1", "1,-1"]))
        if freq == "YEARLY" and rng.random() < 0.1:
            parts.append("BYYEARDAY=" + ",".join(str(x) for x in rng.sample(range(1, 300), 2)))
        if freq == "YEARLY" and rng.random() < 0.1:
            parts.append("BYEASTER=" + rng.choice(["0", "-2", "1"]))
        if freq == "YEARLY" and rng.random() < 0.1:
            parts.append("BYWEEKNO=" + rng.choice(["1", "20", "-1"]))
            parts = [p for p in parts if not p.startswith("BYMONTH")]
        if rng.random() < 0.3:
            parts.append("WKST=" + rng.choice(WD))
    rng.shuffle(parts)
    out = ";".join(parts)
    return out.lower() if low else out


def date_list(rng, n, aware, tzname):
    vals = [dtstr(rng) for _ in range(n)]
    if aware and tzname is None:
        vals = [v + "Z" for v in vals]
    return vals


def set_case(rng, k):
    aware = rng.random() < 0.35
    tzname = rng.choice(TZNAMES) if aware else None
    lines = []
    if aware:
        lines.append("DTSTART;TZID=%s:%s" % (tzname, dtstr(rng)))
    else:
        lines.append(rng.choice(["DTSTART:", "DTSTART;VALUE=DATE-TIME:"]) + dtstr(rng))
    n_dates = rng.randint(max(1, k // 2), k)
    n_rules = rng.randint(1, max(1, n_dates // 20 + 1))
    for _ in range(n_rules):
        lines.append(("RRULE:" if rng.random() < 0.9 else "") + rule(rng, aware))
    for _ in range(rng.randint(0, max(0, n_rules // 3))):
        lines.append("EXRULE:" + rule(rng, aware))
    remaining = n_dates
    while remaining > 0:
        chunk = min(remaining, rng.choice([1, 1, 2, 5, 10]))
        remaining -= chunk
        kind = rng.random()
        if kind < 0.45:
            pre = rng.choice(["RDATE:", "RDATE;VALUE=DATE-TIME:"])
            vals = [v + ("Z" if aware else "") for v in (dtstr(rng) for _ in range(chunk))]
            lines.append(pre + ",".join(vals))
        else:
            if aware and rng.random() < 0.7:
                pre = rng.choice(["EXDATE;TZID=%s:" % tzname, "EXDATE;VALUE=DATE-TIME;TZID=%s:" % tzname])
                vals = [dtstr(rng) for _ in range(chunk)]
            elif aware:
                pre = "EXDATE:"
                vals = [dtstr(rng) + "Z" for _ in range(chunk)]
            else:
                pre = rng.choice(["EXDATE:", "EXDATE;VALUE=DATE-TIME:", "EXDATE;VALUE=DATE:"])
                vals = [dtstr(rng, pre.endswith("DATE:")) for _ in range(chunk)]
            lines.append(pre + ",".join(vals))
    head, body = lines[:1], lines[1:]
    rng.shuffle(body)
    lines = head + body if rng.random() < 0.7 else body[:1] + head + body[1:]
    kw = {}
    r = rng.random()
    if r < 0.15:
        kw["forceset"] = True
    elif r < 0.25:
        kw["compatible"] = True
    if rng.random() < 0.1:
        kw["ignoretz"] = True
    if rng.random() < 0.2:
        kw["cache"] = True
    sep = "\n"
    if rng.random() < 0.3 or kw.get("compatible"):
        # fold long lines (RFC 5545 continuation lines start with a space)
        folded = []
        for ln in lines:
            while len(ln) > 60:
                folded.append(ln[:60])
                ln = " " + ln[60:]
            folded.append(ln)
        if rng.random() < 0.3:
            folded.insert(rng.randint(0, len(folded)), "")
        lines = folded
        kw["unfold"] = True
    s = sep.join(lines)
    if not aware and rng.random() < 0.15:
        s = s.lower()
    return {"s": s, "kw": kw, "dtstart": None, "ti": True}


def single_case(rng):
    form = rng.choice(["bare", "rrule", "dtstart", "dtstart"])
    low = rng.random() < 0.15
    if form == "bare":
        s = rule(rng, False, low)
        ds = [1997, 9, 2, 9, 0, 0]
    elif form == "rrule":
        s = "RRULE:" + rule(rng, False, low)
        ds = [rng.randint(1990, 2020), rng.randint(1, 12), rng.randint(1, 28), 9, 30, 0]
    else:
        s = "DTSTART:%s\nRRULE:%s" % (dtstr(rng), rule(rng, False, low))
        ds = None
        if rng.random() < 0.3:
            s = " " + s.replace("\n", " ") + " "
    kw = {}
    if rng.random() < 0.15:
        kw["forceset"] = True
    if rng.random() < 0.15:
        kw["cache"] = True
    return {"s": s, "kw": kw, "dtstart": ds, "ti": False}


ERRORS = [
    "", "   \n  ",
    "DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=3\nFOO:BAR",
    "DTSTART:19970902T090000\nRRULE;X-NAME=1:FREQ=YEARLY;COUNT=3",
    "DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=3\nRDATE;VALUE=PERIOD:19970904T090000",
    "DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=3\nEXRULE;X=Y:FREQ=DAILY;COUNT=1",
    "DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=3;FOO=1",
    "DTSTART:19970902T090000\nRRULE:FREQ=FORTNIGHTLY;COUNT=3",
    "DTSTART:19970902T090000\nRRULE:FREQ=WEEKLY;BYDAY=;WKST=SU",
    "DTSTART:19970902T090000\nRRULE:FREQ=WEEKLY;BYDAY=-1OK;WKST=SU",
    "DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;UNTIL=TheCowsComeHome",
    "DTSTART:19970101T000000,19970202T000000\nRRULE:FREQ=YEARLY;COUNT=1",
    "DTSTART;TZID=Zone/East:19970902T090000Z\nRRULE:FREQ=YEARLY;COUNT=3",
    "DTSTART;TZID=Zone/East:19970902T090000\nRRULE:FREQ=YEARLY;UNTIL=19990101T000000",
    "DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=3\nEXDATE;VALUE=DATE;VALUE=DATE:19970902",
    "DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=3\nEXDATE;X-FOO=1:19970902T090000",
    "XRULE:FREQ=YEARLY;COUNT=3",
    "DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=x",
]


def cases(n_cases, k, rng, with_errors):
    out = []
    if with_errors:
        for e in ERRORS:
            out.append({"s": e, "kw": {}, "dtstart": [1997, 9, 2, 9, 0, 0], "ti": True})
    while len(out) < n_cases:
        if rng.random() < 0.25:
            out.append(single_case(rng))
        else:
            out.append(set_case(rng, k))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k)) in enumerate(SIZES.items()):
        rng = random.Random(20191103 + i)
        (out_dir / ("workload_%s.json" % size)).write_text(json.dumps(cases(n, k, rng, size == "S")))
