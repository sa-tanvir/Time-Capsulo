"""Seeded workload generator for configFromStringAndFormat(config) (moment(string, format[, strict])).
Usage: python3 gen_workload.py <out_dir>

Each case is [input, format, strict, utc, locale] (locale 'en' or the driver-defined French-like 'tc-fr').
Inputs are rendered from random dates with the same format (date part + time parts, names, ordinals,
meridiem, offsets, ISO week/ordinal dates, long-date macros L/LL/LLL/LLLL/LT), about 35% corrupted
(deleted/replaced characters, extra/leading text, changed separators, changed format, upper case).
S also holds hand-written cases from the test suite (ISO_8601/RFC_2822 constants, bigHour, 24:00, ...).
S/M/L grow the per-call input: formats with ~1 / ~10 / ~100 time groups (input length ~25 / ~150 / ~1,500).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
SIZES = {"S": (2000, 0, 2), "M": (300, 8, 12), "L": (40, 80, 120)}
FIXED = [["2016-01-02T23:40:40.678", "YYYY-MM-DDTHH:mm:ss.SSS", False, False, "en"],
         ["1999 37 Lu", "gggg ww dd", False, False, "tc-fr"], ["2012 july", "YYYY MMM", False, False, "en"],
         ["2012 seven", "YYYY MMM", False, False, "en"], ["2012-05-25", "YYYY-MM-DD", True, False, "en"],
         ["2012-05.25", "YYYY-MM-DD", True, False, "en"], ["2012-05.25", "YYYY-MM-DD", False, False, "en"],
         ["2012-05-25 4 PM", "YYYY-MM-DD h A", True, False, "en"], ["2012-05-25 16 PM", "YYYY-MM-DD h A", False, False, "en"],
         ["2012-05-25 13", "YYYY-MM-DD hh", True, False, "en"], ["2012-05-25 24:00", "YYYY-MM-DD HH:mm", False, False, "en"],
         ["2012-05-25 24:01", "YYYY-MM-DD HH:mm", False, False, "en"], ["2014-02-29", "YYYY-MM-DD", False, False, "en"],
         ["2014-13-01", "YYYY-MM-DD", False, False, "en"], ["2012-05-25T10:00:00+0530", "YYYY-MM-DDTHH:mm:ssZZ", False, True, "en"],
         ["2012 05 25 +05:30", "YYYY MM DD Z", False, False, "en"], ["  2012-05-25", "YYYY-MM-DD", False, False, "en"],
         ["", "YYYY-MM-DD", False, False, "en"], ["12345", "X", False, False, "en"], ["1234567890123", "x", False, True, "en"],
         ["Mon, 25 Dec 1995 13:30:00 +0430", "$RFC", False, False, "en"], ["2013-02-08 09:30:26", "$ISO", False, False, "en"],
         ["2013-02-08 09:30", "$ISO", True, False, "en"], ["Monday 2014-06-03", "dddd YYYY-MM-DD", False, False, "en"],
         ["Tuesday 2014-06-03", "dddd YYYY-MM-DD", False, False, "en"], ["2014 Q3", "YYYY [Q]Q", False, False, "en"],
         ["2014 week 2 day 3", "gggg [week] w [day] e", False, False, "en"], ["2014-007", "YYYY-DDDD", True, False, "en"],
         ["2014-367", "YYYY-DDDD", False, False, "en"], ["2016 12 31 11:59 pm", "YYYY MM DD hh:mm a", True, False, "en"],
         ["2016 12 31 11:59 MD", "YYYY MM DD hh:mm a", False, False, "tc-fr"], ["12/31/2016", "L", True, False, "en"],
         ["31 décembre 2016", "LL", True, False, "tc-fr"], ["20160102", "YYYYMMDD", True, False, "en"],
         ["2016-01-02", "YYYY-MM-DD [extra] HH", True, False, "en"], ["2016-01-02 junk", "YYYY-MM-DD", True, False, "en"],
         ["2016-01-02 11", "YYYY-MM-DD k", False, False, "en"], ["2016-01-02 24", "YYYY-MM-DD kk", False, False, "en"],
         ["2016-1-2 3:4:5.6789", "YYYY-M-D H:m:s.SSSS", False, False, "en"], ["+002016-01-02", "YYYYYY-MM-DD", False, False, "en"]]
# ---- shared generator part: renders (string, format) pairs for moment parsing formats
import datetime

EN_M = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
EN_MS = [m[:3] for m in EN_M]
EN_W = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
EN_WS = [w[:3] for w in EN_W]
EN_WM = [w[:2] for w in EN_W]
FR_M = "janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre".split("_")
FR_MS = "janv._févr._mars_avr._mai_juin_juil._août_sept._oct._nov._déc.".split("_")
FR_W = "dimanche_lundi_mardi_mercredi_jeudi_vendredi_samedi".split("_")
FR_WS = "dim._lun._mar._mer._jeu._ven._sam.".split("_")
FR_WM = "di_lu_ma_me_je_ve_sa".split("_")
NAMES = {"en": (EN_M, EN_MS, EN_W, EN_WS, EN_WM), "tc-fr": (FR_M, FR_MS, FR_W, FR_WS, FR_WM)}


def ordinal(n):
    if 10 <= n % 100 <= 20:
        return "%dth" % n
    return "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def render_token(tok, dt, loc, off):
    M, MS, W, WS, WM = NAMES[loc]
    wd = (dt.weekday() + 1) % 7  # 0 = Sunday
    h12 = dt.hour % 12 or 12
    t = {
        "YYYY": "%04d" % dt.year, "YY": "%02d" % (dt.year % 100), "Y": str(dt.year),
        "M": str(dt.month), "MM": "%02d" % dt.month, "MMM": MS[dt.month - 1], "MMMM": M[dt.month - 1],
        "D": str(dt.day), "DD": "%02d" % dt.day, "Do": ordinal(dt.day) if loc == "en" else str(dt.day),
        "DDD": str(dt.timetuple().tm_yday), "DDDD": "%03d" % dt.timetuple().tm_yday,
        "d": str(wd), "dd": WM[wd], "ddd": WS[wd], "dddd": W[wd],
        "H": str(dt.hour), "HH": "%02d" % dt.hour, "h": str(h12), "hh": "%02d" % h12,
        "k": str(dt.hour or 24), "kk": "%02d" % (dt.hour or 24),
        "a": ("am" if dt.hour < 12 else "pm") if loc == "en" else ("PD" if dt.hour < 12 else "MD"),
        "A": ("AM" if dt.hour < 12 else "PM") if loc == "en" else ("PD" if dt.hour < 12 else "MD"),
        "m": str(dt.minute), "mm": "%02d" % dt.minute, "s": str(dt.second), "ss": "%02d" % dt.second,
        "S": str(dt.microsecond // 100000), "SS": "%02d" % (dt.microsecond // 10000), "SSS": "%03d" % (dt.microsecond // 1000),
        "SSSS": "%04d" % (dt.microsecond // 100),
        "Z": ("+" if off >= 0 else "-") + "%02d:%02d" % divmod(abs(off), 60),
        "ZZ": ("+" if off >= 0 else "-") + "%02d%02d" % divmod(abs(off), 60),
        "Q": str((dt.month - 1) // 3 + 1),
        "E": str(dt.isoweekday()), "W": str(dt.isocalendar()[1]), "WW": "%02d" % dt.isocalendar()[1],
        "GGGG": "%04d" % dt.isocalendar()[0],
    }
    return t[tok]


DATE_PARTS = [["YYYY", "-", "MM", "-", "DD"], ["YYYY", "/", "M", "/", "D"], ["DD", ".", "MM", ".", "YYYY"],
              ["MMMM", " ", "Do", ", ", "YYYY"], ["MMM", " ", "D", " ", "YYYY"], ["dddd", ", ", "MMMM", " ", "D", " ", "YYYY"],
              ["ddd", " ", "DD", " ", "MMM", " ", "YYYY"], ["YYYY", "", "MM", "", "DD"], ["YYYY", "-", "DDDD"],
              ["GGGG", "-[W]", "WW", "-", "E"], ["D", "/", "M", "/", "YY"], ["Q", "[Q] ", "YYYY"], ["YYYY", " ", "MMMM"],
              ["dd", " ", "D", " ", "MMMM", " ", "YYYY"], ["YYYY", "-", "M", "-", "D", " ", "d"]]
TIME_PARTS = [[], ["HH", ":", "mm"], ["HH", ":", "mm", ":", "ss"], ["HH", ":", "mm", ":", "ss", ".", "SSS"],
              ["h", ":", "mm", " ", "a"], ["hh", ":", "mm", ":", "ss", " ", "A"], ["H", "", "mm"], ["kk", ":", "mm"],
              ["HH", ":", "mm", " ", "Z"], ["HH", ":", "mm", ":", "ss", "ZZ"], ["h", " ", "A"], ["HH", ":", "mm", ":", "ss", ",", "SS"]]
TOKENS = {"YYYY", "YY", "Y", "M", "MM", "MMM", "MMMM", "D", "DD", "Do", "DDD", "DDDD", "d", "dd", "ddd", "dddd", "H", "HH",
          "h", "hh", "k", "kk", "a", "A", "m", "mm", "s", "ss", "S", "SS", "SSS", "SSSS", "Z", "ZZ", "Q", "E", "W", "WW", "GGGG"}


def fmt_escape(lit):
    if lit == "" or lit.startswith("["):
        return lit
    if any(c.isalpha() for c in lit):
        return "[" + lit + "]"
    return lit


def render(parts, dt, loc, off):
    s, f = "", ""
    for p in parts:
        if p in TOKENS:
            s += render_token(p, dt, loc, off)
            f += p
        else:
            f += p if "[" in p else fmt_escape(p)
            s += p.replace("[", "").replace("]", "")
    return s, f


def rand_dt(rng):
    y = rng.choice([rng.randint(1900, 2100), rng.randint(1000, 9999), rng.randint(1970, 2030)])
    d = datetime.datetime(y, 1, 1) + datetime.timedelta(days=rng.randint(0, 364), seconds=rng.randint(0, 86399),
                                                      microseconds=rng.randint(0, 999) * 1000)
    if d.year != y:
        d = d.replace(year=y, month=12, day=31)
    return d


def corrupt(rng, s, f):
    r = rng.random()
    if r < 0.2 and s:
        i = rng.randrange(len(s))
        s = s[:i] + s[i + 1:]
    elif r < 0.35:
        s = s + rng.choice([" extra", "!", " 12", "  ", "Z", " pm"])
    elif r < 0.5:
        s = rng.choice(["x ", " ", "on ", "1 "]) + s
    elif r < 0.6 and s:
        i = rng.randrange(len(s))
        s = s[:i] + rng.choice("0123456789 -:/aZ") + s[i + 1:]
    elif r < 0.7:
        s = s.replace("-", "/", 1)
    elif r < 0.8:
        f = f.replace("DD", "D", 1).replace("MM", "M", 1)
    elif r < 0.9:
        s = s.upper()
    else:
        f = f + rng.choice([" HH", " [at] LT", " SSS", " x"])
    return s, f


def one_pair(rng, loc, time_reps):
    dt = rand_dt(rng)
    off = rng.choice([0, 60, -300, 330, 545, -720, 840])
    date = rng.choice(DATE_PARTS)
    parts = list(date)
    tp = rng.choice(TIME_PARTS)
    for _ in range(time_reps):
        if tp:
            parts += [" "] + tp
            tp = rng.choice(TIME_PARTS[1:])
    s, f = render(parts, dt, loc, off)
    if rng.random() < 0.08:
        f = rng.choice(["L", "LL", "LLL", "LLLL", "L LT", "LL LTS"]) if rng.random() < 0.5 else f
        if f in ("L", "LL", "LLL", "LLLL", "L LT", "LL LTS"):
            lf = {"en": {"L": "MM/DD/YYYY", "LL": "MMMM D, YYYY", "LLL": "MMMM D, YYYY h:mm A",
                         "LLLL": "dddd, MMMM D, YYYY h:mm A", "L LT": "MM/DD/YYYY h:mm A", "LL LTS": "MMMM D, YYYY h:mm:ss A"},
                  "tc-fr": {"L": "DD/MM/YYYY", "LL": "D MMMM YYYY", "LLL": "D MMMM YYYY HH:mm",
                            "LLLL": "dddd D MMMM YYYY HH:mm", "L LT": "DD/MM/YYYY HH:mm", "LL LTS": "D MMMM YYYY HH:mm:ss"}}[loc][f]
            import re as _re
            toks = _re.findall(r"\[[^\]]*\]|Do|YYYY|MMMM|MMM|MM|M|dddd|DD|D|HH|H|hh|h|mm|ss|A|[^A-Za-z]+", lf)
            s, _ = render([t if t in TOKENS else t for t in toks], dt, loc, off)
    if rng.random() < 0.35:
        s, f = corrupt(rng, s, f)
    return s, f


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, (size, (n, rlo, rhi)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cases = list(FIXED) if size == "S" else []
        while len(cases) < n:
            loc = rng.choice(["en", "en", "tc-fr"])
            s, f = one_pair(rng, loc, rng.randint(rlo, rhi))
            cases.append([s, f, rng.random() < 0.4, rng.random() < 0.3, loc])
        (out / f"workload_{size}.json").write_text(json.dumps({"cases": cases}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
