"""Seeded workload generator for humanize.ParseBigBytes. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, max fractional digits): per-case string length grows ~10x per size
SIZES = {"S": (6_000, 8), "M": (6_000, 80), "L": (6_000, 800)}
EDGE = ["42", "42MB", "42MiB", "42mb", "42mib", "42MIB", "42 MB", "42 MiB", "42 mb", "42 mib", "42 MIB",
        "42.5MB", "42.5MiB", "42.5 MB", "42.5 MiB", "42M", "42Mi", "42m", "42mi", "42MI", "42 M", "42 Mi",
        "42 m", "42 mi", "42 MI", "42.5M", "42.5Mi", "42.5 M", "42.5 Mi", "1,005.03 MB", "12.5 EB", "12.5 E",
        "12.5 EiB", "84 JB", "", "16 EiB", ".", "5.", ".5", "1.2.3", "1,,2", ",", "0", "42 kB ", "  42", "-5",
        "1e3", "18446744073709551615", "15.99 EiB", "16 ZB", "16 ZiB", "16.5 ZB", "16.5 ZiB", "16 Z", "16 Zi", "16.5 Z",
        "16.5 Zi", "16 YB", "16 YiB", "16.5 YB", "16.5 YiB", "16 Y", "16 Yi", "16.5 Y", "16.5 Yi",
        "0.000000000000000000001 YB", "1 B", "1 bytes", "0.9", "1.9999999", "007", "1,0.5k", "3 \tk"]
UNITS = ["", "b", "k", "kb", "ki", "kib", "m", "mb", "mi", "mib", "g", "gb", "gi", "gib", "t", "tb", "ti", "tib",
         "p", "pb", "pi", "pib", "e", "eb", "ei", "eib", "z", "zb", "zi", "zib", "y", "yb", "yi", "yib"]
BAD_UNITS = ["jb", "bytes", "xb", "yy", "kbit", "mm"]

def rcase(rng, u):
    return "".join(c.upper() if rng.random() < 0.5 else c for c in u)

def case(rng, maxfrac):
    r = rng.random()
    unit = rng.choice(UNITS) if r < 0.93 else rng.choice(BAD_UNITS)
    nint = rng.randint(1, max(3, maxfrac // 2))  # no 64-bit limit: integer part scales too
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
