"""Seeded workload generator for Locale#weekdaysParse (localeWeekdaysParse(weekdayName, format, strict)).
Usage: python3 gen_workload.py <out_dir>

Each case is [locale, weekdayName, format, strict]. Locales: 'en' and driver-defined ones (French-like
names with periods, the same with weekdaysParseExact, names containing '.', format/standalone names,
exact-mode names that are prefixes of each other). Names: exact full/short/min names in random case,
names with trailing text, names with/without periods, prefixes, unknown words. format is 'dddd', 'ddd',
'dd', another token or undefined; strict is true, false or undefined.
Per-call work is bounded (7 weekdays), so S/M/L scale the call count: 2,000 / 20,000 / 200,000
(L = 50,000 distinct cases used 4 times).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
U = {"$undef": 1}
SIZES = {"S": (2000, 1), "M": (20000, 1), "L": (50000, 4)}
NAMES = {
    "en": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
           "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
    "tc-fr": ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dim.", "lun.", "mar.",
              "mer.", "jeu.", "ven.", "sam.", "Di", "Lu", "Ma", "Me", "Je", "Ve", "Sa"],
    "tc-periods": ["Sunday", "T....day", "Thursday", "Mon.day", "Monday", "Monxday", "t...s", "thurs", "m.n", "mn",
                   "man", "t..", "tue", "su", "we", "th", "mo"],
    "tc-fmt": ["Sunday", "Monday", "mondayF", "Friday", "Sun", "Mon", "S", "M", "T", "W", "F"],
    "tc-prefix-exact": ["Ab", "Abc", "Abcd", "B", "Bc", "C", "Cd", "a", "ab", "abc", "b", "bc", "c", "cd", "A", "AB",
                        "X", "Y", "Z"],
}
NAMES["tc-fr-exact"] = NAMES["tc-fr"]
LOCALES = list(NAMES)
JUNK = ["", "x", "Funday", "lundis", "1", "Mo.", "dim", "MONDAY!", "  Monday", "Tuesday 12", "jeu", "Sa.", "Abcde"]
FORMATS = ["dddd", "dddd", "ddd", "ddd", "dd", "dd", "d", U]

FIXED = [["en", "Monday", "dddd", True], ["en", "monday", "dddd", True], ["en", "Mon", "dddd", True],
         ["en", "Mon", "ddd", True], ["en", "Mo", "dd", True], ["en", "Monday", U, U], ["en", "Mozart", "dd", False],
         ["en", "Friyay", "ddd", False], ["en", "xyz", "dddd", False], ["en", "Mon", "d", True],
         ["tc-fr", "lun.", "ddd", True], ["tc-fr", "lun", "ddd", True], ["tc-fr", "lundi", "dddd", False],
         ["tc-fr", "Lu", "dd", True], ["tc-fr", "dim.", "ddd", False], ["tc-fr-exact", "LUNDI", "dddd", True],
         ["tc-fr-exact", "lun.", "dddd", False], ["tc-fr-exact", "Lu", "ddd", False], ["tc-fr-exact", "lun", "ddd", False],
         ["tc-fr-exact", "Lu", "dd", True], ["tc-fr-exact", "Lu", "d", True], ["tc-periods", "thurs", "ddd", True],
         ["tc-periods", "Thursday", "dddd", True], ["tc-periods", "t...s", "ddd", True], ["tc-periods", "Monxday", "dddd", True],
         ["tc-periods", "Monday", "dddd", True], ["tc-periods", "mn", "ddd", True], ["tc-periods", "man", "ddd", False],
         ["tc-fmt", "mondayF", "dddd", True], ["tc-fmt", "Monday", "dddd", True], ["tc-prefix-exact", "Abc", "dddd", True],
         ["tc-prefix-exact", "abc", "ddd", False], ["tc-prefix-exact", "X", "dd", False], ["tc-prefix-exact", "Cd", "dddd", False]]


def name(rng, loc):
    r = rng.random()
    s = rng.choice(NAMES[loc])
    if r < 0.6:
        pass
    elif r < 0.7:
        s = s.upper() if rng.random() < 0.5 else s.lower()
    elif r < 0.8:
        s = s + rng.choice([" ", "x", " 12", ".", "day"])
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
        (out / f"workload_{size}.json").write_text(json.dumps({"times": times, "cases": cases}, separators=(",", ":")))
