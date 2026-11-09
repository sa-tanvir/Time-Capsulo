"""Seeded workload generator (pattern_formatter::compile_pattern_). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. Line: <secs nanos level namelen payloadlen line seed tid msgid> TAB pattern (last field, may be empty). Patterns mix literal text, flags (never %P), padding specs, %%, unknown flags, colour markers and a trailing lone %. Pattern length grows 10x / 100x for M/L.
"""
import random, sys
from pathlib import Path

SEED = 20190118   # release date of spdlog 1.3.1 as an int; size i uses SEED + i

FLAGS_SAFE = "nlLtvaAbBhcCYDxmdHIMSeEfFprRTXzi^$@s#!%"
def msg_fields(rng, scale):
    """secs nanos level namelen payloadlen line seed tid msgid (as list of str)"""
    secs = rng.randrange(1000000000, 2100000000)
    nanos = rng.choice([0, 1, 999999999, rng.randrange(0, 1000000000), rng.randrange(0, 1000000000)])
    level = rng.randrange(0, 7)
    namelen = rng.choice([0, 1, 4, 9, rng.randrange(0, 12 * scale + 1)])
    paylen = rng.choice([0, 1, rng.randrange(0, 40 * scale + 1), rng.randrange(0, 40 * scale + 1)])
    line = rng.choice([0, 0, rng.randrange(1, 100000)])
    return [secs, nanos, level, namelen, paylen, line, rng.randrange(1, 10**6), rng.randrange(1, 10**7), rng.randrange(0, 10**7)]

LIT = "abcdefghijklmnopqrstuvwxyz0123456789 []:-,.()/<>@#"
def rnd_pattern(rng, target):
    out = []
    n = 0
    while n < target:
        r = rng.random()
        if r < 0.45:
            tok = "".join(rng.choice(LIT) for _ in range(rng.randrange(1, 7)))
        else:
            pad = ""
            q = rng.random()
            if q < 0.2:
                pad = str(rng.choice([1, 3, 6, 10, 20, 150]))
            elif q < 0.35:
                pad = "-" + str(rng.choice([2, 5, 9, 16, 128, 300]))
            elif q < 0.5:
                pad = "=" + str(rng.choice([3, 4, 8, 11]))
            elif q < 0.53:
                pad = rng.choice(["-", "="])
            flag = rng.choice(FLAGS_SAFE) if rng.random() < 0.88 else rng.choice("kKgjqQuwyZ0] _")
            tok = "%" + pad + flag
        out.append(tok)
        n += len(tok)
    s = "".join(out)
    if rng.random() < 0.08:
        s += "%"
    return s

def lines(size, rng):
    scale = {"S": 1, "M": 1, "L": 1}[size]
    target, n = {"S": (30, 300), "M": (300, 800), "L": (3000, 600)}[size]
    out = []
    if size == "S":
        for p in ["", "%", "%%", "%v", "%^%v%$", "[%Y-%m-%d %H:%M:%S.%e] [%n] [%l] %v", "%-10l|%=8L|%12n|%v", "%x %X %+", "%]", "%5", "%-", "%=", "abc%", "%300v", "%-300n", "%^", "%$"]:
            out.append("\t".join([str(x) for x in msg_fields(rng, 1)] + [p]))
    for _ in range(n):
        t = rng.randrange(max(1, target // 3), target + 1)
        out.append("\t".join([str(x) for x in msg_fields(rng, 1)] + [rnd_pattern(rng, t)]))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
