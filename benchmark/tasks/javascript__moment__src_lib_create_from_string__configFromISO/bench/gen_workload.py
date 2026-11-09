"""Seeded workload generator for configFromISO(config) (ISO 8601 detection for moment(string)).
Usage: python3 gen_workload.py <out_dir>

Each case is [input, {"$undef":1}, strict, utc, 'en'] (no format, as for moment(string) / moment.utc(string);
strict only matters for the final format-based parse). Inputs: extended and basic calendar dates,
6-digit signed years, week dates, ordinal dates, year-month, with 'T' or space times (hh, hh:mm,
hh:mm:ss, fractions with '.' or ',', basic forms), zones (Z, +hh, +hh:mm, +hhmm), leading whitespace,
plus near-misses (time after a date form that forbids it, bad time forms, out-of-range parts, junk).
Each input has bounded length, so S/M/L scale the call count: 2,000 / 20,000 / 200,000
(L = 40,000 distinct cases used 5 times).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
U = {"$undef": 1}
SIZES = {"S": (2000, 1), "M": (20000, 1), "L": (40000, 5)}

FIXED = ["2013-02-08", "2013-W06-5", "2013-039", "20130208", "2013W065", "2013W06", "2013050", "2013-02",
         "2013-02-08T09", "2013-02-08 09", "2013-02-08T09:30", "2013-02-08 09:30:26", "2013-02-08 09:30:26.123",
         "2013-02-08 09:30:26,123", "2013-02-08T09:30:26.123+07:00", "2013-02-08T09:30:26.123-0700",
         "2013-02-08T09:30:26.123+07", "2013-02-08T09:30:26 Z", "2013-02-08T0930", "2013-02-08T093026",
         "2013-02-08T093026.123", "20130208T080910,123", "20130208T080910.123+0700", "+002013-02-08",
         "-002013-02-08", "+0020130208", "2013-W06", "2013-W06T09", "2013-02T09:00", "2013-02-08T9:30",
         "2013-02-08T09:3", "  2013-02-08", "2013-02-08 ", "2013-13-01", "2013-02-30", "2013-366", "2012-366",
         "2013-02-08T24:00", "2013-02-08T24:00:01", "2013-02-08T25:00", "2013-02-08T09:60", "2013-W54-1",
         "2013-W00-1", "2013-W06-8", "2010-10-20T10:20:30.40+05:00", "2010-10-20T10:20:30.40-1530", "201310",
         "2013-02-08T09:30:26.123456789", "2013/02/08", "nope", "", "2013-02-08T", "2013-02-08X09:30",
         "2013-02-08T09:30:26+07:00:00", "2013-02-08T09:30:26+7", "2013-02-08 09:30:26   Z"]


def one(rng):
    y = rng.choice([rng.randint(1900, 2100), rng.randint(0, 9999)])
    mo, d = rng.randint(1, 12), rng.randint(1, 31 if rng.random() < 0.2 else 28)
    r = rng.random()
    ext = rng.random() < 0.7
    allow_time = True
    if r < 0.45:
        date = ("%04d-%02d-%02d" if ext else "%04d%02d%02d") % (y, mo, d)
    elif r < 0.55:
        w, e = rng.randint(1, 53), rng.randint(1, 7)
        date = ("%04d-W%02d-%d" if ext else "%04dW%02d%d") % (y, w, e)
    elif r < 0.62:
        date = ("%04d-W%02d" if ext else "%04dW%02d") % (y, rng.randint(1, 53))
        allow_time = False
    elif r < 0.72:
        date = ("%04d-%03d" if ext else "%04d%03d") % (y, rng.randint(1, 366))
    elif r < 0.8:
        date = "%04d-%02d" % (y, mo)
        allow_time = False
    elif r < 0.85:
        date = ("%s%06d-%02d-%02d" if ext else "%s%06d%02d%02d") % (rng.choice("+-"), rng.randint(0, 275000), mo, d)
    else:
        date = "%04d-%02d-%02d" % (y, mo, d)
    s = date
    if rng.random() < (0.7 if allow_time else 0.1):
        h, mi, se = rng.randint(0, 24 if rng.random() < 0.05 else 23), rng.randint(0, 59), rng.randint(0, 59)
        sep = ":" if ext else ""
        t = "%02d" % h
        k = rng.random()
        if k < 0.8:
            t += sep + "%02d" % mi
        if k < 0.6:
            t += sep + "%02d" % se
        if k < 0.3:
            t += rng.choice([".", ","]) + str(rng.randint(0, 999999))[: rng.randint(1, 6)]
        s += rng.choice(["T", "T", " "]) + t
        z = rng.random()
        if z < 0.2:
            s += rng.choice(["Z", " Z"])
        elif z < 0.5:
            hh, mm = rng.randint(0, 14), rng.choice([0, 30, 45])
            s += rng.choice("+-") + rng.choice(["%02d:%02d" % (hh, mm), "%02d%02d" % (hh, mm), "%02d" % hh])
    if rng.random() < 0.12:
        i = rng.randrange(len(s))
        s = s[:i] + rng.choice(["", "x", "-", ":", "9", " "]) + s[i + 1:]
    if rng.random() < 0.03:
        s = rng.choice([" ", "  ", "\t"]) + s
    return s


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, (size, (n, times)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        strs = list(FIXED) if size == "S" else []
        while len(strs) < n:
            strs.append(one(rng))
        cases = [[s, U, rng.random() < 0.2, rng.random() < 0.3, "en"] for s in strs]
        (out / f"workload_{size}.json").write_text(json.dumps({"times": times, "cases": cases}, separators=(",", ":")))
