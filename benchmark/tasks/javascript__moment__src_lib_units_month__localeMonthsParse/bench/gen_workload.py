"""Seeded workload generator for Locale#monthsParse (localeMonthsParse(monthName, format, strict)).
Usage: python3 gen_workload.py <out_dir>

Each case is [locale, monthName, format, strict]. Locales: 'en' and driver-defined ones (French-like names
with periods, the same with monthsParseExact, a Russian-like locale with preset parse regexes and
format/standalone names, a locale with periods inside names, exact-mode names that are prefixes of each
other). Names: exact long/short names in random case, with trailing text, truncated, unknown words.
format is 'MMMM', 'MMM', 'M' or undefined; strict is true, false or undefined.
Per-call work is bounded (12 months), so S/M/L scale the call count: 2,000 / 20,000 / 200,000
(L = 50,000 distinct cases used 4 times).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
U = {"$undef": 1}
SIZES = {"S": (2000, 1), "M": (20000, 1), "L": (50000, 4)}
EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
      "November", "December", "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
NAMES = {
    "en": EN,
    "tc-fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "décembre",
              "janv.", "janv", "févr.", "avr.", "juil.", "juil", "sept.", "sept", "déc.", "dec"],
    "tc-ru": ["января", "январь", "янв.", "мая", "май", "июня", "июнь", "июля", "сент.", "сентябрь", "дек.", "декабря"],
    "tc-fmt": ["January", "Jan.uary", "Janxuary", "ofJan", "March", "J.n", "Jan", "Jxn", "M.y", "May", "Mzy", "D.c"],
    "tc-prefix-exact": ["A", "AA", "AAA", "B", "B B", "BB  B", "C", "C-C", "C,C2C", "D", "D+D", "D`D*D",
                        "E", "EE", "EEE", "F", "FF", "GGG", "HHH", "a", "bb  b"],
}
NAMES["tc-fr-exact"] = NAMES["tc-fr"]
LOCALES = list(NAMES)
JUNK = ["", "x", "Smarch", "13", "Ma", "Ju", "MAYDAY", "  May", "May 12", "Sept", "j", "Decembers"]
FORMATS = ["MMMM", "MMMM", "MMM", "MMM", "M", U]

FIXED = [["en", "March", "MMMM", True], ["en", "march", "MMMM", True], ["en", "Mar", "MMMM", True],
         ["en", "Mar", "MMM", True], ["en", "March", "MMM", True], ["en", "Marchxx", "MMM", False], ["en", "May", U, U],
         ["en", "Ma", U, U], ["en", "xyz", "MMM", False], ["en", "Mar", "M", True], ["en", "Sept", "MMM", False],
         ["tc-fr", "janv.", "MMM", True], ["tc-fr", "janv", "MMM", True], ["tc-fr", "janvx", "MMM", False],
         ["tc-fr", "juil.", "MMM", True], ["tc-fr", "juin", "MMMM", False], ["tc-fr-exact", "JANV.", "MMM", True],
         ["tc-fr-exact", "janv", "MMM", True], ["tc-fr-exact", "janvier", "MMM", False], ["tc-fr-exact", "janv.", "MMMM", False],
         ["tc-fr-exact", "janv.", "MMMM", True], ["tc-fr-exact", "xx", "MMM", False], ["tc-ru", "мая", "MMMM", True],
         ["tc-ru", "май", "MMM", False], ["tc-ru", "июля", "MMMM", True], ["tc-fmt", "Janxuary", "MMMM", True],
         ["tc-fmt", "ofJan", "MMMM", False], ["tc-prefix-exact", "AA", "MMMM", True], ["tc-prefix-exact", "BB  B", "MMMM", True],
         ["tc-prefix-exact", "EE", "MMMM", False], ["tc-prefix-exact", "A", "MMM", False]]


def name(rng, loc):
    r = rng.random()
    s = rng.choice(NAMES[loc])
    if r < 0.6:
        pass
    elif r < 0.7:
        s = s.upper() if rng.random() < 0.5 else s.lower()
    elif r < 0.8:
        s = s + rng.choice([" ", "x", " 12", ".", "s"])
    elif r < 0.9:
        s = s[: rng.randint(1, max(1, len(s) - 1))]
    else:
        s = rng.choice(JUNK)
    return s


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, (size, (n, times)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cases = list(FIXED) if size == "S" else []
        while len(cases) < n:
            loc = rng.choice(LOCALES)
            cases.append([loc, name(rng, loc), rng.choice(FORMATS), rng.choice([True, False, False, U])])
        (out / f"workload_{size}.json").write_text(json.dumps({"times": times, "cases": cases}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
