"""Seeded workload generator for tzical._parse_rfc. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, VTIMEZONE blocks per case): per-case text size grows ~10x per size
SIZES = {"S": (40, 1), "M": (40, 10), "L": (40, 100)}

EST = """BEGIN:VTIMEZONE
TZID:US-Eastern
LAST-MODIFIED:19870101T000000Z
TZURL:http://zones.stds_r_us.net/tz/US-Eastern
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19870405T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
END:DAYLIGHT
END:VTIMEZONE"""


def offset(rng):
    h, m = rng.randint(0, 13), rng.choice([0, 0, 15, 30, 45])
    sign = rng.choice(["+", "-", "-", ""])
    if rng.random() < 0.1:
        return "%s%02d%02d%02d" % (sign, h, m, rng.randint(0, 59))
    return "%s%02d%02d" % (sign, h, m)


def dtstart(rng):
    return "%04d%02d%02dT%02d%02d%02d" % (rng.randint(1900, 2010), rng.randint(1, 12), rng.randint(1, 28),
                                         rng.randint(0, 3), rng.choice([0, 0, 30]), 0)


def component(rng, kind):
    lines = ["BEGIN:" + kind]
    body = []
    dt = dtstart(rng)
    body.append(rng.choice(["DTSTART:", "DTSTART;VALUE=DATE-TIME:", "dtstart:"]) + dt)
    r = rng.random()
    if r < 0.7:
        rr = "RRULE:FREQ=YEARLY;BYDAY=%s%dSU;BYMONTH=%d" % (rng.choice(["", "+", "-"]), rng.randint(1, 2),
                                                             rng.randint(1, 12))
        if rng.random() < 0.3:
            rr += ";UNTIL=%04d1231T235959" % rng.randint(2011, 2030)
        body.append(rr)
    elif r < 0.85:
        body.append("RDATE:" + ",".join(dtstart(rng) for _ in range(rng.randint(1, 3))))
    if rng.random() < 0.15:
        body.append("EXDATE:" + dtstart(rng))
    body.append("TZOFFSETFROM:" + offset(rng))
    body.append(rng.choice(["TZOFFSETTO:", "tzoffsetto:"]) + offset(rng))
    if rng.random() < 0.85:
        body.append("TZNAME:" + rng.choice(["EST", "EDT", "CET", "CEST", "Z%d" % rng.randint(0, 99), "A:B"]))
    if rng.random() < 0.3:
        body.append("COMMENT:some comment; with: colons")
    rng.shuffle(body)
    lines += body
    lines.append("END:" + kind)
    return lines


def vtimezone(rng, idx):
    lines = ["BEGIN:VTIMEZONE"]
    head = ["TZID:Zone/%d-%d" % (idx, rng.randint(0, 9999))]
    if rng.random() < 0.4:
        head.append("LAST-MODIFIED:19870101T000000Z")
    if rng.random() < 0.3:
        head.append("TZURL:http://example.org/tz/%d" % idx)
    rng.shuffle(head)
    lines += head
    for _ in range(rng.randint(1, 3)):
        lines += component(rng, rng.choice(["STANDARD", "DAYLIGHT"]))
    lines.append("END:VTIMEZONE")
    return lines


def fold(lines, rng):
    out = []
    for ln in lines:
        if len(ln) > 12 and rng.random() < 0.2:
            k = rng.randint(1, len(ln) - 1)
            out += [ln[:k], " " + ln[k:]]
        else:
            out.append(ln)
        if rng.random() < 0.05:
            out.append("   ")
    return out


ERRORS = [
    "", "BEGIN:VTIMEZONE\nTZID:X\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nBEGIN:STANDARD\nDTSTART:19671029T020000\nTZOFFSETFROM:-0400\nTZOFFSETTO:-0500\nEND:STANDARD\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nDTSTART:19671029T020000\nTZOFFSETFROM:-0400\nTZOFFSETTO:-0500\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nTZOFFSETFROM:-0400\nTZOFFSETTO:-0500\nEND:STANDARD\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nDTSTART:19671029T020000\nTZOFFSETTO:-0500\nEND:STANDARD\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nDTSTART:19671029T020000\nTZOFFSETFROM:-0500\nEND:STANDARD\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nDTSTART;VALUE=DATE:19671029\nTZOFFSETFROM:-0400\nTZOFFSETTO:-0500\nEND:STANDARD\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nDTSTART;TZID=UTC:19671029T020000\nTZOFFSETFROM:-0400\nTZOFFSETTO:-0500\nEND:STANDARD\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:WEIRD\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nEND:STANDARD\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nDTSTART:19671029T020000\nTZOFFSETFROM:-0400\nTZOFFSETTO:-0500\nEND:DAYLIGHT",
    "BEGIN:VTIMEZONE\nTZID;X=Y:X\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nFOO:bar\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nX-FOO:bar\nEND:STANDARD",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nTZOFFSETFROM;A=B:-0400",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nTZOFFSETTO;A=B:-0400",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nTZNAME;LANGUAGE=en:EST",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nTZOFFSETFROM:-04000",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nTZOFFSETFROM:  ",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nRRULE:FREQ=YEARLY;FOO=1\nDTSTART:19671029T020000\nTZOFFSETFROM:-0400\nTZOFFSETTO:-0500\nEND:STANDARD",
    EST + "\nBEGIN:VTIMEZONE\nTZID:Y\nFOO:bar",
    "PRODID:x\nBEGIN:VCALENDAR\nFOO:bar\nEND:VCALENDAR",
    "   \n\n  ",
    EST + "\n" + EST.replace("EST", "XST"),
    EST + "\nBEGIN:VTIMEZONE\nTZID:Open\nBEGIN:STANDARD\nDTSTART:19671029T020000\nTZOFFSETFROM:-0400\nTZOFFSETTO:-0500\nEND:STANDARD",
    "BEGIN:VTIMEZONE\nTZID:X\nBEGIN:STANDARD\nDTSTART:19671029T020000\nBEGIN:DAYLIGHT\nDTSTART:19870405T020000\nTZOFFSETFROM:-0500\nTZOFFSETTO:-0400\nEND:DAYLIGHT\nEND:VTIMEZONE",
    " BEGIN:VTIMEZONE\nTZID:X\nEND:VTIMEZONE",
    "BEGIN:VTIMEZONE\nTZID:\nBEGIN:STANDARD\nDTSTART:19671029T020000\nTZOFFSETFROM:-0400\nTZOFFSETTO:-0500\nEND:STANDARD\nEND:VTIMEZONE",
    "begin:VTIMEZONE\ntzid:lower\nbegin:STANDARD\ndtstart:19671029T020000\ntzoffsetfrom:+0100\ntzoffsetto:+013015\nend:STANDARD\nend:VTIMEZONE",
    "BEGIN:vtimezone\nTZID:X\nFOO:bar",
]


def gen(n_cases, n_zones, rng, with_fixed):
    out = list(ERRORS) if with_fixed else []
    while len(out) < n_cases:
        lines = []
        if rng.random() < 0.5:
            lines += ["BEGIN:VCALENDAR", "PRODID:-//Test//EN", "VERSION:2.0"]
        for z in range(n_zones):
            lines += vtimezone(rng, z)
        if lines[0] == "BEGIN:VCALENDAR":
            lines.append("END:VCALENDAR")
        sep = rng.choice(["\n", "\r\n"])
        out.append(sep.join(fold(lines, rng)) + sep)
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, z)) in enumerate(SIZES.items()):
        rng = random.Random(20191103 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(gen(n, z, rng, size == "S")))
