"""Seeded workload generator for isFQDN(str, options). Usage: python3 gen_workload.py <out_dir>

Each case is an argument list [str, options?]. Long strings are encoded compactly as
{"$cat": [...]} / {"$rep": [s, n]} and expanded by the driver.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20191121
# (random cases, labels per name range): mean name length ~25 / ~250 / ~2500 characters
SIZES = {"S": (300, (1, 5)), "M": (300, (20, 60)), "L": (300, (250, 550))}

LOWER = "abcdefghijklmnopqrstuvwxyz"
LDH = LOWER + LOWER.upper() + "0123456789-"
UNI = "äöüßéñçøåмюлер端日本語"
TLDS = ["com", "org", "co", "plato", "blackfriday", "xn--p1ai", "xn--90ais", "рф", "端端", "COM", "museum"]
BAD_TLDS = ["c", "1com", "xn-", "co m", "c　m", "com ", "x﻿y", "c0m", "\U000e0020ab", "-com"]
OPTS = [None, {}, {"require_tld": False}, {"allow_underscores": True}, {"allow_trailing_dot": True},
        {"require_tld": False, "allow_underscores": True, "allow_trailing_dot": True}, {"require_tld": True}]

FIXED = [
    "domain.com", "dom.plato", "a.domain.co", "foo--bar.com", "xn--froschgrn-x9a.com", "rebecca.blackfriday",
    "abc", "256.0.0.0", "_.com", "*.some.com", "s!ome.com", "domain.com/", "/more.com", "example.com.",
    "example.com..", "", ".", "..", "a..b.com", ".com", "com.", "-a.com", "a-.com", "a_b.com", "a__.com", "__.com",
    "localhost", "my_host", "ｇｍａｉｌ.com", "gmail.ｃｏｍ", "m端ller.com", "a.b.c.d.e.f.g.h", "foo.c", "foo.co m",
    "foo.co　m", "foo.xn--", "foo.xn--a", "foo.xn--ab", "a" * 63 + ".com", "a" * 64 + ".com", "foo." + "c" * 63,
    "foo." + "c" * 64, "under_score.example.com", "UPPER.CASE.COM", "1.2.3.4", "123.com", "a.1com", "foo.é",
    "foo. x", "foo. x", "x¡y.com", "a b.com", "tab\t.com", "trailing.dot.", "x.", "x..", "foo.bar_",
]


def label(rng, alphabet, lo=1, hi=12):
    n = rng.randint(lo, hi)
    s = "".join(rng.choice(alphabet) for _ in range(n))
    if rng.random() < 0.9:
        s = s.strip("-") or "a"
    return s


def name(rng, nlab):
    labs = []
    for _ in range(nlab):
        r = rng.random()
        if r < 0.75:
            labs.append(label(rng, LDH))
        elif r < 0.9:
            labs.append(label(rng, LOWER + UNI))
        else:
            labs.append(label(rng, LOWER + "_"))
    if rng.random() < 0.85:
        labs.append(rng.choice(TLDS))
    else:
        labs.append(rng.choice(BAD_TLDS))
    s = ".".join(labs)
    if rng.random() < 0.15:
        s += "."
    if rng.random() < 0.05:
        i = rng.randrange(len(s))
        s = s[:i] + rng.choice("!*/ 　ｇ") + s[i:]
    return s


def opt(rng):
    o = rng.choice(OPTS)
    return [] if o is None else [dict(o)]


def cases(n, labs, rng, with_fixed):
    out = []
    if with_fixed:
        for s in FIXED:
            for o in OPTS:
                out.append([s] + ([] if o is None else [dict(o)]))
        for bad in [None, 123, ["a.com"]]:
            out.append([bad])
    for _ in range(n):
        nl = rng.randint(*labs)
        if nl > 50:
            # repeat a block of labels to keep the workload file small
            block = name(rng, 20)
            block = block[:block.rfind(".") + 1] if "." in block else block + "."
            s = {"$cat": [{"$rep": [block, nl // 20]}, name(rng, rng.randint(1, 5))]}
        else:
            s = name(rng, nl)
        out.append([s] + opt(rng))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, labs)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, labs, rng, size == "S")))
