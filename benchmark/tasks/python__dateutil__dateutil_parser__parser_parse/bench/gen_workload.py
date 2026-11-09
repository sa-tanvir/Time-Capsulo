"""Seeded workload generator for parser._parse. Usage: python3 gen_workload.py <out_dir>

Each case: a date/time core string embedded in filler whose length grows ~10x per size
(jump-word filler for strict cases, free text for fuzzy cases), plus dayfirst/yearfirst/fuzzy flags."""
import json, random, sys
from pathlib import Path

N_CASES = 200
FILLER = {"S": 2, "M": 40, "L": 400}          # filler words per case
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONL = ["January", "February", "March", "April", "May", "June", "July", "August",
        "September", "October", "November", "December"]
DAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAYL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
JUMPS = [" ", " ", " ", ", ", " on ", " at ", " and ", "; ", " , "]
WORDS = ["today", "is", "the", "meeting", "report", "exactly", "with", "timezone", "about",
         "quarterly", "notes", "from", "team", "see", "you", "there", "schedule", "update",
         "review", "office", "Project", "Budget", "a", "at", "on", "and", "of", "http://x.io/p/q.html",
         "(draft)", "~", "Room", "deadline"]
TZS = ["", "", "", " UTC", " Z", " GMT", " BRST", " -0300", " +05:30", " -03:00 (BRST)", " PST", " GMT+3", " +02"]
EDGE = [
    ("", {}), ("shouldfail", {}), ("AM", {}), ("13:44 AM", {}), ("NaN", {}), ("1: test", {}),
    ("201A-01-01T23:58:39", {}), ("04/04/32/423", {"fuzzy_with_tokens": True}),
    ("04/04/04 +32423", {"fuzzy_with_tokens": True}), ("04/04/0d4", {"fuzzy_with_tokens": True}),
    ("Sep of 03", {}), ("Jan-01-99", {}), ("090107", {"dayfirst": True, "yearfirst": True}),
    ("I have a meeting on March 1, 1974.", {"fuzzy": True}),
    ("Meet me at the AM/PM on Sunset at 3:00 AM on December 3rd, 2003", {"fuzzy": True}),
    ("http://biz.yahoo.com/ipo/p/600221.html", {"fuzzy_with_tokens": True}),
    ("12h 01m02s am", {}), ("10:00a.m.", {}), ("5:50 A.M. on June 13, 1990", {}),
    ("2016-12-21 04.2h", {}), ("Jan 20, 2015 PM", {}), ("2017-07-17 06:15:", {"fuzzy": True}),
    ("02:17NOV2017", {}), ("AD2001", {}), ("December.0031.30", {}), ("Feb 30, 2007", {}),
]


def core(rng):
    y = rng.randint(1900, 2099); m = rng.randint(1, 12); d = rng.randint(1, 28)
    H = rng.randint(0, 23); M = rng.randint(0, 59); S = rng.randint(0, 59)
    us = rng.randint(0, 999999); h12 = H % 12 or 12; ap = rng.choice(["am", "pm", "AM", "PM", "a.m.", "p.m."])
    fmts = [
        "%04d-%02d-%02dT%02d:%02d:%02d" % (y, m, d, H, M, S),
        "%04d-%02d-%02dT%02d:%02d:%02d.%06d" % (y, m, d, H, M, S, us),
        "%04d%02d%02dT%02d%02d%02d" % (y, m, d, H, M, S),
        "%04d%02d%02d" % (y, m, d),
        "%04d%02d%02d%02d%02d" % (y, m, d, H, M),
        "%s %s %2d %02d:%02d:%02d %04d" % (DAY[rng.randrange(7)], MON[m - 1], d, H, M, S, y),
        "%s, %d %s %04d %02d:%02d:%02d" % (DAY[rng.randrange(7)], d, MON[m - 1], y, H, M, S),
        "%s %d, %04d %d:%02d %s" % (MONL[m - 1], d, y, h12, M, ap),
        "%02d/%02d/%04d" % (m, d, y), "%02d.%02d.%02d" % (d, m, y % 100), "%02d-%s-%04d" % (d, MON[m - 1], y),
        "%04d/%s/%02d" % (y, MON[m - 1], d), "%d %s %04d" % (d, MONL[m - 1], y),
        "%dh%02dm%02ds" % (H, M, S), "%d%s" % (h12, ap), "%d:%02d:%02d,%03d" % (H, M, S, us // 1000),
        "%s %d%s of %04d" % (DAYL[rng.randrange(7)], d, rng.choice(["st", "nd", "rd", "th"]), y),
        "%02d%02d%02d %02d%02d%02d" % (y % 100, m, d, H, M, S), "%s of %02d" % (MONL[m - 1], y % 100),
        "%04d %02d %02d %02d:%02d" % (y, m, d, H, M),
    ]
    timed = [0, 1, 2, 4, 5, 6, 7, 13, 14, 15, 17, 19]     # formats that set an hour (tz suffix allowed)
    j = rng.randrange(len(fmts))
    return fmts[j] + (rng.choice(TZS) if j in timed else "")


def case(rng, nfill):
    fuzzy = rng.random() < 0.5
    if fuzzy:
        pick = lambda: " " + rng.choice(WORDS) + " "
    else:
        pick = lambda: rng.choice(JUMPS)
    k = rng.randint(0, nfill)
    pre = "".join(pick() for _ in range(k))
    post = "".join(pick() for _ in range(nfill - k))
    kw = {"dayfirst": rng.choice([None, False, True]), "yearfirst": rng.choice([None, False, True])}
    if fuzzy:
        kw["fuzzy_with_tokens" if rng.random() < 0.5 else "fuzzy"] = True
    return [pre + core(rng) + post, kw]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191103 + i)
        cases = [list(e) for e in EDGE] if size == "S" else []
        while len(cases) < N_CASES:
            cases.append(case(rng, FILLER[size]))
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases))
