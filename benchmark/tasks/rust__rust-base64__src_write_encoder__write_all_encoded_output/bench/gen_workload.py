"""Seeded workload generator for base64 EncoderWriter::write_all_encoded_output. Usage: python3 gen_workload.py <out_dir>

One case per line, tab separated: <pending_len> <seed> <cap> <intr> <fail_at>
driver.rs fills output[..pending_len] with base64 symbols from <seed>; the delegate accepts at most <cap> bytes per
call (0 = all; 1 in ~10 calls it accepts 0 bytes when <cap> > 0), returns Interrupted on every <intr>-th call (0 = never)
and ErrorKind::Other on call number <fail_at> (0 = never).
"""
import random, sys
from pathlib import Path

# pending bytes, per-call cap range
SIZES = {"S": (300, (0, 64), (0, 64)), "M": (300, (256, 1024), (16, 96)), "L": (300, (1000, 1024), (1, 6))}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191025 + i)
        n, (lo, hi), (clo, chi) = SIZES[size]
        lines = []
        for _ in range(n):
            pend = rng.randint(lo, hi)
            cap = rng.randint(clo, chi)
            intr = rng.choice([0, 0, rng.randint(2, 6)])
            fail_at = rng.choice([0] * 9 + [rng.randint(1, 12)])
            lines.append("%d\t%d\t%d\t%d\t%d" % (pend, rng.randrange(1, 2**63), cap, intr, fail_at))
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")
