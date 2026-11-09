"""Seeded workload generator for _rrulestr._parse_date_value. Usage: python3 gen_workload.py <out_dir>

Each case: {"value": comma-separated dates, "parms": [...], "rule_tzids": {UPPER: Original},
"ignoretz": bool, "tzids": "map"|"call"|"none"|"bad", "ti": bool}. The driver maps the tzids
kind to a fixed dict / callable of tzoffset objects ("none" is only used when no TZID lookup can
happen). Dates per case grow ~10x per size.
"""
import json, random, sys
from pathlib import Path

SIZES = {"S": (80, 10), "M": (60, 100), "L": (60, 1000)}   # (cases, max dates per case)
TZNAMES = ["Zone/East", "Zone/West", "Mid-Atlantic", "UTC", "Unmapped/Zone"]


def dt(rng, form):
    y, m, d = rng.randint(1900, 2099), rng.randint(1, 12), rng.randint(1, 28)
    H, M, S = rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59)
    if form == "date":
        return "%04d%02d%02d" % (y, m, d)
    if form == "iso":
        return "%04d-%02d-%02dT%02d:%02d:%02d" % (y, m, d, H, M, S)
    return "%04d%02d%02dT%02d%02d%02d" % (y, m, d, H, M, S)


def case(rng, k):
    n = rng.randint(max(1, k // 2), k)
    form = rng.choice(["basic", "basic", "basic", "date", "iso"])
    rule_tzids = {}
    for name in rng.sample(TZNAMES, rng.randint(0, 3)):
        rule_tzids[name.upper()] = name
    parms = []
    use_tz = rule_tzids and rng.random() < 0.6
    if use_tz:
        key = rng.choice(list(rule_tzids))
        parms.append("TZID=" + key)
    elif rng.random() < 0.2:
        parms.append("TZID=NOT-DECLARED")      # not in rule_tzids -> ignored
    vp = rng.random()
    if vp < 0.4:
        parms.insert(rng.randint(0, len(parms)), "VALUE=DATE" if form == "date" else "VALUE=DATE-TIME")
    suffix = ""
    if not use_tz and rng.random() < 0.4:
        suffix = rng.choice(["Z", " XYZ", "+0130", "-05:00"])
        if form == "date":
            form = "basic"
    vals = [dt(rng, form) + suffix for _ in range(n)]
    tzids = rng.choice(["map", "map", "call"]) if parms and any(p.startswith("TZID=") for p in parms) \
        else rng.choice(["map", "call", "none"])
    if tzids == "none" and any(p.startswith("TZID=") and p[5:] in rule_tzids for p in parms):
        tzids = "map"
    return {"value": ",".join(vals), "parms": parms, "rule_tzids": rule_tzids,
            "ignoretz": rng.random() < 0.15, "tzids": tzids, "ti": True}


def errors():
    rt = {"ZONE/EAST": "Zone/East"}
    base = {"rule_tzids": rt, "ignoretz": False, "tzids": "map", "ti": True}
    out = []
    for value, parms, extra in [
        ("19970902T090000", ["VALUE=PERIOD"], {}),
        ("19970902T090000", ["X-FOO=BAR"], {}),
        ("19970902", ["VALUE=DATE", "VALUE=DATE"], {}),
        ("19970902T090000", ["VALUE=DATE-TIME", "TZID=ZONE/EAST", "VALUE=DATE-TIME"], {}),
        ("19970902T090000Z", ["TZID=ZONE/EAST"], {}),
        ("19970902T090000,19970903T090000+0200", ["TZID=ZONE/EAST"], {}),
        ("19970902T090000", ["TZID=ZONE/EAST"], {"tzids": "bad"}),
        ("19970902T090000", ["TZID=ZONE/EAST"], {"tzids": "raise"}),
        ("TheCowsComeHome", [], {}),
        ("19970902T090000,", [], {}),
        ("19970902T090000Z", ["TZID=ZONE/EAST"], {"ignoretz": True}),
        ("19970902T090000", ["TZID=NOT-DECLARED"], {"tzids": "bad"}),
        ("19970902T090000,19970904T090000,19970911T090000", [], {"tzids": "none"}),
        ("19970902T090000", ["VALUE=DATE-TIME", "TZID=ZONE/EAST"], {"tzids": "call"}),
        ("19970902T090000 XYZ", [], {"ti": False}),
    ]:
        c = dict(base, value=value, parms=parms)
        c.update(extra)
        out.append(c)
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k)) in enumerate(SIZES.items()):
        rng = random.Random(20191103 + i)
        cs = errors() if size == "S" else []
        while len(cs) < n:
            cs.append(case(rng, k))
        (out_dir / ("workload_%s.json" % size)).write_text(json.dumps(cs))
