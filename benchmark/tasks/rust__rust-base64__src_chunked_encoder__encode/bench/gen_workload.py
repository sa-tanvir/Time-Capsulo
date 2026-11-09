"""Seeded workload generator for base64 ChunkedEncoder::encode. Usage: python3 gen_workload.py <out_dir>

One case per line, tab separated:
  lit <charset S|U|C> <pad 0|1> <hex of the raw input>
  gen <charset> <pad> <raw_len> <seed>     (driver.rs expands <raw_len> xorshift64* bytes from <seed>)
"""
import random, sys
from pathlib import Path

LITS = [b"", b"f", b"fo", b"foo", b"foobar", b"foobarf", b"foobarbazqux", b"foobarbazquxquuxcorgegraultgarplyz",
        bytes([0, 1, 2, 3]), b"hello world~", b"hello internet~", bytes([255]), bytes([255, 254]), bytes(range(256))]
SIZES = {"S": (300, (0, 100)), "M": (300, (500, 2500)), "L": (300, (5000, 25000))}
# lengths around the 765/768-byte chunk boundary
EDGE = [764, 765, 766, 767, 768, 769, 1530, 1531, 1536, 1537]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191025 + i)
        n, (lo, hi) = SIZES[size]
        lines = []
        if size == "S":
            for s in LITS:
                for cs in "SUC":
                    for pad in "01":
                        lines.append("lit\t%s\t%s\t%s" % (cs, pad, s.hex()))
        if size == "M":
            for L in EDGE:
                for pad in "01":
                    lines.append("gen\tS\t%s\t%d\t%d" % (pad, L, rng.randrange(1, 2**63)))
        for _ in range(n):
            lines.append("gen\t%s\t%s\t%d\t%d" % (rng.choice("SUC"), rng.choice("01"), rng.randint(lo, hi),
                                                  rng.randrange(1, 2**63)))
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")
