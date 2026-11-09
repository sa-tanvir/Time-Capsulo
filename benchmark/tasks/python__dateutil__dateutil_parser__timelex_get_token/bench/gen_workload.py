"""Seeded workload generator for _timelex.get_token. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, pieces per case): per-case string length grows ~10x per size
SIZES = {"S": (300, 4), "M": (300, 40), "L": (300, 400)}

FIXED = ["Thu Sep 25 10:36:28 BRST 2003", "2003-09-25T10:49:41.5-03:00", "Sep.20.2009",
         "4:30:21.447", "10:36:28,123", "1999.12", "0.5", "12.34.56", "12.", "ab.", "12,",
         "3rd of May 2001", "July 4, 1976 12:01:02 am", "12,345", "12,3,4", "1,234.5", "12,5.3",
         "5.6a", "1.2a", "a.1", "x.12,5", "3.c4", "1.a", "1.a ", "1.ab", "12,a", "...", "a..b",
         "", " x\t\ny ", "\x00a\x00b", "1,5", "a1", "1a", "é.ü", "a.b.c", "1.2.a",
         "Sep.", "h.1.2", "x.y1", "1..2", "a.12.3", "12a.b", "a.b1", "1 . 2", "12.5,"]
WORDS = ["Sep", "September", "Thu", "Thursday", "am", "pm", "BRST", "UTC", "of", "the", "rd",
         "st", "T", "Z", "h", "m", "s", "a.m.", "p.m.", "jan", "Déc", "at", "on"]
SEPS = [" ", " ", " ", "  ", "\t", "\n", ",", ", ", "-", "/", ":", "+", "."]


def piece(rng):
    k = rng.random()
    if k < 0.25:
        return rng.choice(WORDS)
    if k < 0.45:
        return str(rng.randint(0, 99999))
    if k < 0.55:
        return "%d.%d" % (rng.randint(0, 99), rng.randint(0, 9999))
    if k < 0.62:
        return "%d,%d" % (rng.randint(0, 99), rng.randint(0, 999))
    if k < 0.72:
        return "%02d:%02d:%02d.%d" % (rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59), rng.randint(0, 999999))
    if k < 0.80:
        return "%s.%d.%d" % (rng.choice(WORDS), rng.randint(1, 31), rng.randint(1900, 2100))
    if k < 0.86:
        return "%d-%02d-%02dT%02d:%02d" % (rng.randint(1900, 2100), rng.randint(1, 12), rng.randint(1, 28),
                                           rng.randint(0, 23), rng.randint(0, 59))
    if k < 0.93:
        alpha = "ab1.,"
        return "".join(rng.choice(alpha) for _ in range(rng.randint(1, 6)))
    return rng.choice(FIXED)


def gen(n_cases, n_pieces, rng, with_fixed):
    out = list(FIXED) if with_fixed else []
    while len(out) < n_cases:
        parts = []
        for _ in range(n_pieces):
            parts.append(piece(rng))
            parts.append(rng.choice(SEPS))
        out.append("".join(parts[:-1]))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, p)) in enumerate(SIZES.items()):
        rng = random.Random(20191103 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(gen(n, p, rng, size == "S")))
