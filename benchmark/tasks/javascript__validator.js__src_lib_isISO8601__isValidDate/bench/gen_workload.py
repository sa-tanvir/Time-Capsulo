"""Seeded workload generator for isValidDate(str) (strict ISO 8601 date check).
Usage: python3 gen_workload.py <out_dir>

Every input already matches the library's ISO 8601 pattern (the function's precondition); years are
1000-9999. Each case is an argument list [str]. Per-call input size is bounded, so S/M/L grow in case count.
"""
import json, random, re, sys
from pathlib import Path

RELEASE = 20191121
SIZES = {"S": 2000, "M": 20000, "L": 200000}

ISO = re.compile(r"^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-3])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$")

FIXED = ["2009-12T12:34", "2009", "2009-05-19", "20090519", "2009123", "2009-05", "2009-123", "2009-222", "2009-001",
         "2009-W01-1", "2009-W51-1", "2009-W511", "2009-W33", "2009W511", "2009-05-19 00:00", "2009-05-19 14",
         "2009-05-19 14:31", "2009-05-19 14:39:22", "2009-05-19T14:39Z", "2009-W21-2", "2009-W21-2T01:22", "2009-139",
         "2009-05-19 14:39:22-06:00", "2009-05-19 14:39:22+0600", "2009-05-19 14:39:22-01", "20090621T0545Z",
         "2007-04-06T00:00", "2007-04-05T24:00", "2010-02-18T16:23:48.5", "2010-02-18T16:23:48,444",
         "2010-02-18T16:23:48,3-06:00", "2010-02-18T16:23.4", "2010-02-18T16:23,25", "2010-02-18T16:23.33+0600",
         "2010-02-18T16.23334444", "2010-02-18T16,2283", "2009-05-19 143922.500", "2009-05-19 1439,55", "2009-10-10",
         "2020-366", "2000-366", "2000-02-29", "2400-366", "2010-02-30", "2009-02-29", "2009-366", "2019-02-31",
         "2100-02-29", "2100-366", "1900-366", "2004-366", "2009-000", "2009-04-31", "2009-06-31", "2009-11-31",
         "2009-12-31", "2009-01-31", "20090229", "20000229", "2009-365T10:00", "2009365", "2009366", "2008366",
         "+2009-02-29", "-2008-02-29", "2009-02-29T25", "2009-02", "1000-01-01", "9999-12-31", "2009-02-28T24:00"]


def ymd(rng, y):
    m = rng.randint(1, 12)
    d = rng.choice([rng.randint(1, 28), rng.randint(29, 31), rng.randint(1, 31)])
    return m, d


def one(rng):
    y = rng.choice([rng.randint(1000, 9999), rng.randint(1890, 2110), rng.choice([1900, 2000, 2100, 2400, 1600, 2004])])
    r = rng.random()
    if r < 0.2:
        doy = rng.choice([rng.randint(1, 366), rng.randint(360, 366)])
        s = "%04d%s%03d" % (y, rng.choice(["-", ""]), doy)
    elif r < 0.3:
        s = "%04d-W%02d-%d" % (y, rng.randint(1, 53), rng.randint(1, 7))
    elif r < 0.4:
        s = "%04d-%02d" % (y, rng.randint(1, 12))
    else:
        m, d = ymd(rng, y)
        sep = rng.choice(["-", "-", ""])
        s = "%04d%s%02d%s%02d" % (y, sep, m, sep, d)
    if rng.random() < 0.4:
        t = rng.choice(["T", " "]) + "%02d:%02d" % (rng.randint(0, 23), rng.randint(0, 59))
        if rng.random() < 0.5:
            t += ":%02d" % rng.randint(0, 59)
            if rng.random() < 0.3:
                t += "." + str(rng.randint(0, 999999))
        t += rng.choice(["", "Z", "+01:00", "-0530", "+02"])
        s += t
    if rng.random() < 0.03:
        s = rng.choice(["+", "-"]) + s
    return s


def cases(n, rng, with_fixed):
    out = []
    if with_fixed:
        out += [[s] for s in FIXED if ISO.match(s)]
    while len(out) < n:
        s = one(rng)
        if ISO.match(s):
            out.append([s])
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, n) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, rng, size == "S")))
