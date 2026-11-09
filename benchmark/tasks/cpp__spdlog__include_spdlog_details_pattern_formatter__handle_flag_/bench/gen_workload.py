"""Seeded workload generator (pattern_formatter::handle_flag_). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. Line: flag TAB width TAB side TAB <secs nanos level namelen payloadlen line seed tid msgid>. flag is one printable character (P, the process id, is never generated). S: every known flag with several paddings plus unknown characters; M/L: more random cases with longer names/payloads.
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

KNOWN = FLAGS_SAFE
UNKNOWN = "kKgGjJNOoqQuUwWyYZ0123456789 ]_-,.;:'\"<>=+*&~`?{}()[]|/"

def one(rng, scale, flag=None):
    if flag is None:
        flag = rng.choice(KNOWN) if rng.random() < 0.85 else rng.choice(UNKNOWN)
    w = rng.choice([0, 0, 0, 1, 5, 8, 12, 30, 128, rng.randrange(0, 129)])
    return "\t".join([flag, str(w), rng.choice("lrc")] + [str(x) for x in msg_fields(rng, scale)])

def lines(size, rng):
    scale = {"S": 1, "M": 10, "L": 100}[size]
    out = []
    if size == "S":
        for f in KNOWN + UNKNOWN:
            for _ in range(2):
                out.append(one(rng, scale, f))
    n = {"S": 100, "M": 20000, "L": 100000}[size]
    out += [one(rng, scale) for _ in range(n)]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
