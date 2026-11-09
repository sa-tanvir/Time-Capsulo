"""Seeded workload generator for humanize.ParseBytes. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, max fractional digits): per-case string length grows ~10x per size
SIZES = {"S": (6_000, 8), "M": (6_000, 80), "L": (6_000, 800)}
EDGE = ["42", "42MB", "42MiB", "42mb", "42mib", "42MIB", "42 MB", "42 MiB", "42 mb", "42 mib", "42 MIB",
        "42.5MB", "42.5MiB", "42.5 MB", "42.5 MiB", "42M", "42Mi", "42m", "42mi", "42MI", "42 M", "42 Mi",
        "42 m", "42 mi", "42 MI", "42.5M", "42.5Mi", "42.5 M", "42.5 Mi", "1,005.03 MB", "12.5 EB", "12.5 E",
        "12.5 EiB", "84 JB", "", "16 EiB", ".", "5.", ".5", "1.2.3", "1,,2", ",", "0", "42 kB ", "  42", "-5",
        "1e3", "18446744073709551615", "1 B", "1 bytes", "0.9", "1.9999999", "007", "1,0.5k", "3 \tk"]
UNITS = ["", "b", "k", "kb", "ki", "kib", "m", "mb", "mi", "mib", "g", "gb", "gi", "gib", "t", "tb", "ti", "tib",
         "p", "pb", "pi", "pib", "e", "eb", "ei", "eib"]
BAD_UNITS = ["jb", "bytes", "zb", "y", "kbit", "mm"]
# max integer digits that stay below 2^64 bytes for each unit's power
POW = {"": 0, "b": 0, "k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}

def rcase(rng, u):
    return "".join(c.upper() if rng.random() < 0.5 else c for c in u)

def case(rng, maxfrac):
    r = rng.random()
    unit = rng.choice(UNITS) if r < 0.93 else rng.choice(BAD_UNITS)
    p = POW.get(unit[:1], 0)
    maxint = max(1, 19 - 3 * p)
    nint = rng.randint(1, maxint + (1 if rng.random() < 0.1 else 0))  # occasionally too large
    ip = str(rng.randint(1, 9)) + "".join(rng.choice("0123456789") for _ in range(nint - 1))
    if rng.random() < 0.3 and len(ip) > 3:
        head = len(ip) % 3 or 3
        ip = ip[:head] + "".join("," + ip[k:k + 3] for k in range(head, len(ip), 3))
    frac = ""
    if rng.random() < 0.8:
        frac = "." + "".join(rng.choice("0123456789") for _ in range(rng.randint(0, maxfrac)))
    sp = rng.choice(["", "", " ", "  ", "\t"])
    tail = rng.choice(["", "", " "])
    return ip + frac + sp + rcase(rng, unit) + tail

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, maxfrac)) in enumerate(SIZES.items()):
        rng = random.Random(20180713 + i)
        vals = list(EDGE) if size == "S" else []
        while len(vals) < n:
            vals.append(case(rng, maxfrac))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"values": vals}))
