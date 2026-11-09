"""Seeded workload generator for configFromStringAndArray(config) (moment(string, [formats...][, strict])).
Usage: python3 gen_workload.py <out_dir>

Each case is [input, formats, strict, utc, locale] (locale 'en' or the driver-defined French-like 'tc-fr').
The input is rendered from a random date with one format (possibly corrupted); the format list mixes that
format with formats rendered for other inputs, near variants (fewer tokens, extra tokens, other
separators) and formats that cannot match, and the ISO_8601 / RFC_2822 constants ("$ISO" / "$RFC"). S also holds cases from the test suite.
S/M/L grow the number of formats per call: ~3 / ~30 / ~300.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
SIZES = {"S": (1500, 1, 5), "M": (300, 15, 45), "L": (40, 200, 400)}
FIXED = [["13-14-1999", ["MM-DD-YYYY", "DD-MM-YYYY"], False, False, "en"],
         ["13-13-1999", ["MM-DD-YYYY", "DD-MM-YYYY"], False, False, "en"],
         ["11-02-1999", ["MM/DD/YYYY", "YYYY MM DD"], False, False, "en"],
         ["1999-11-02", ["YYYY-MM-DD", "YYYY-DD-MM"], False, False, "en"],
         ["13-11-1999", ["MM/DD/YYYY", "DD/MM/YYYY"], False, False, "en"],
         ["11-02-10", ["MM/DD/YY", "YY MM DD", "DD-MM-YY"], False, False, "en"],
         ["2012-05-25", [], False, False, "en"], ["2012-05-25", ["YYYY-MM-DD HH:mm", "YYYY-MM-DD"], True, False, "en"],
         ["2012-05-25 10:20", ["YYYY-MM-DD", "YYYY-MM-DD HH:mm"], False, False, "en"],
         ["2012-05-25 10:20", ["YYYY-MM-DD", "YYYY-MM-DD HH:mm"], True, True, "en"],
         ["foo", ["YYYY", "MM"], False, False, "en"], ["10:20", ["HH:mm", "YYYY HH:mm"], False, False, "en"],
         ["2016 x", ["YYYY", "YYYY [x]", "YYYY MM"], False, False, "en"], ["2016 x", ["YYYY", "YYYY [x]"], True, False, "en"],
         ["Monday 2014-06-03", ["dddd YYYY-MM-DD", "YYYY-MM-DD"], False, False, "en"],
         ["12/31/2016", ["L", "LL"], False, False, "en"], ["1994", ["$ISO", "MM", "HH:mm", "YYYY"], False, False, "en"],
         ["17:15", ["$ISO", "MM", "HH:mm", "YYYY"], False, False, "en"], ["2013-02-08 09:30", ["MM", "$ISO"], True, False, "en"],
         ["Mon, 25 Dec 1995 13:30:00 +0430", ["$ISO", "$RFC"], False, False, "en"], [" ", ["MM", "DD"], False, False, "en"],
         ["01", ["MM", "DD"], False, False, "en"], ["13-10-98", ["DD MM YY", "DD MM YYYY"], False, False, "en"],
         ["11-02-10 junk", ["MM-DD-YY", "YY.MM.DD [junk]"], False, False, "en"], ["11-22-10", ["YY-MM-DD", "YY-DD-MM"], False, False, "en"], ["31 décembre 2016", ["L", "LL"], False, False, "tc-fr"]]
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


def variant(rng, f):
    r = rng.random()
    if r < 0.3:
        return f.replace("-", "/").replace(".", "-")
    if r < 0.5:
        return f.rsplit(" ", 1)[0] if " " in f else f + " HH"
    if r < 0.7:
        return f.replace("DD", "MM", 1) if "DD" in f else f.replace("YYYY", "YY")
    if r < 0.85:
        return f + rng.choice([" HH:mm", ":ss", " [x]", " Z"])
    return rng.choice(["X", "x", "HH:mm", "[never]", "Q", "YYYY [Q]Q", "$ISO", "$RFC"])


def case(rng, nlo, nhi):
    loc = rng.choice(["en", "en", "tc-fr"])
    s, f = one_pair(rng, loc, rng.randint(0, 2))
    fmts = []
    n = rng.randint(nlo, nhi)
    while len(fmts) < n - 1:
        r = rng.random()
        if r < 0.5:
            fmts.append(variant(rng, f))
        else:
            fmts.append(one_pair(rng, loc, rng.randint(0, 2))[1])
    if rng.random() < 0.85:
        fmts.insert(rng.randint(0, len(fmts)), f)
    return [s, fmts, rng.random() < 0.3, rng.random() < 0.3, loc]


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cases = list(FIXED) if size == "S" else []
        while len(cases) < n:
            cases.append(case(rng, lo, hi))
        (out / f"workload_{size}.json").write_text(json.dumps({"cases": cases}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
