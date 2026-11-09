"""Seeded workload generator for chooseLocale(names) (locale fallback for moment.locale([...])).
Usage: python3 gen_workload.py <out_dir>

The driver defines the locales in "locales" ('en' is built in). Each case is a list of requested
locale names: known locales, unknown variants of known roots ('fr-crap', 'en-gb-leeds'), unknown
roots ('fake-CA'), mixed case and '_' separators, sometimes no match at all.
S/M/L grow the list length (~3 / ~30 / ~300 names, the match, if any, tends to be late).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
SIZES = {"S": (1500, 3), "M": (600, 30), "L": (200, 300)}
LOCALES = ["en", "en-gb", "en-ca", "en-au", "fr", "fr-ca", "fr-ch", "es", "es-do", "de", "de-at", "de-ch",
           "zh-cn", "zh-tw", "zh-hk", "pt", "pt-br", "sr", "sr-cyrl", "x-pseudo", "tzm-latn", "ar-sa", "nl-be"]
ROOTS = sorted({l.split("-")[0] for l in LOCALES})
FAKE = ["fake", "xx", "qq", "klingon", "zz", "abc", "foo"]

FIXED = [["non-existent", "fr", "also-non-existent"], ["es", "fr", "also-non-existent"], ["fr-crap"],
         ["fr-does-not-exist"], ["fr-CA-does-not-exist"], ["en-CH", "fr"], ["en-gb-leeds", "en-CA"],
         ["en-fake", "en-CA"], ["en-fake", "en-fake2", "en-ca"], ["fake-CA", "fake-MX", "fr"],
         ["fake-CA", "fake-MX", "fr-fake-fake-fake"], ["en", "en-CA"], [], ["nope"], ["ZH_TW"], ["zh_tw-x"],
         ["sr-Cyrl-ME"], ["x-pseudo-y", "x-other"], ["de-AT"], ["de-li", "de-ch"], ["de-li", "fr-ch"],
         ["tzm-latn-ma"], ["pt-pt", "pt-br"], ["a-b-c-d-e-f", "a-b-c-d-e-g", "fr"], ["fake-ca", "xx-ca"]]


def variant(rng, root):
    parts = [root] + [rng.choice(["ca", "gb", "us", "crap", "leeds", "cyrl", "latn", "x", "br", "at", "ch", "ma"])
                      for _ in range(rng.randint(1, 3))]
    s = "-".join(parts)
    r = rng.random()
    if r < 0.2:
        s = s.upper()
    elif r < 0.3:
        s = s.replace("-", "_", 1)
    return s


def name(rng, p_known):
    r = rng.random()
    if r < p_known:
        return rng.choice(LOCALES)
    if r < p_known + 0.4:
        return variant(rng, rng.choice(ROOTS))
    return variant(rng, rng.choice(FAKE)) if rng.random() < 0.7 else rng.choice(FAKE)


def case(rng, n):
    n = max(1, rng.randint(n // 2, n * 3 // 2))
    names = [variant(rng, rng.choice(FAKE)) for _ in range(n)]
    # a few real candidates, biased towards the end
    for _ in range(rng.randint(0, 3)):
        pos = int(n * (1 - rng.random() ** 3)) if n > 1 else 0
        names[min(pos, n - 1)] = name(rng, 0.3)
    return names


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, (size, (count, n)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cases = (list(FIXED) if size == "S" else []) + [case(rng, n) for _ in range(count)]
        (out / f"workload_{size}.json").write_text(json.dumps({"locales": LOCALES, "cases": cases}, separators=(",", ":")))
