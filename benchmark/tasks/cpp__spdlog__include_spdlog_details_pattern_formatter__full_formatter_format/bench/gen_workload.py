"""Seeded workload generator (full_formatter::format). Usage: python3 gen_workload.py <out_dir>

Writes workload_S.txt, workload_M.txt, workload_L.txt. Line: secs nanos level name_length payload_length line seed thread_id msg_id (payload/name/file/function text is synthesised by the driver). line 0 = no source location; name_length 0 = empty logger name. Name/payload lengths grow with the size.
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

def lines(size, rng):
    scale = {"S": 1, "M": 10, "L": 100}[size]
    n = {"S": 300, "M": 3000, "L": 6000}[size]
    out = []
    for _ in range(n):
        out.append("\t".join(str(x) for x in msg_fields(rng, scale)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(SEED + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
