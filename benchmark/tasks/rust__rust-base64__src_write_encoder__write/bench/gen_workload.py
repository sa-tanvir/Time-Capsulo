"""Seeded workload generator for base64 EncoderWriter::write. Usage: python3 gen_workload.py <out_dir>

One case per line, tab separated: <charset S|U|C> <pad 0|1> <data_len> <seed> <max_write> <cap> <intr>
driver.rs expands <data_len> xorshift64* bytes from <seed> and a cyclic list of write sizes in [0, max_write];
the delegate accepts at most <cap> bytes per call (0 = all) and fails with Interrupted on every <intr>-th call
(0 = never). The caller retries Interrupted errors and keeps writing until all data is consumed, then finishes.
"""
import random, sys
from pathlib import Path

SIZES = {"S": (300, (0, 200), (1, 10)), "M": (300, (2000, 8000), (10, 300)), "L": (300, (20000, 80000), (100, 3000))}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191025 + i)
        n, (lo, hi), (wlo, whi) = SIZES[size]
        lines = []
        for _ in range(n):
            r = rng.random()
            if r < 0.5:
                cap, intr = 0, 0
            elif r < 0.75:
                cap, intr = rng.randint(1, 1100), 0
            else:
                cap, intr = rng.choice([0, rng.randint(1, 1100)]), rng.randint(2, 7)
            lines.append("%s\t%s\t%d\t%d\t%d\t%d\t%d" % (rng.choice("SUC"), rng.choice("01"), rng.randint(lo, hi),
                                                         rng.randrange(1, 2**63), rng.randint(wlo, whi), cap, intr))
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")
