"""Seeded workload generator for base64 decode_helper. Usage: python3 gen_workload.py <out_dir>

One case per line, tab separated:
  lit  <charset S|U|C> <allow_trailing 0|1> <hex of the encoded input>
  gen  <charset> <allow_trailing> <pad 0|1> <raw_len> <seed> <mutation>
`gen` cases are expanded by driver.rs: <raw_len> pseudo-random bytes (xorshift64*, seeded) are encoded with the
crate's encode_config, then <mutation> is applied: `none`, `set:<pos>:<byte>` (overwrite one encoded byte) or
`cut:<k>` (drop the last k encoded bytes).
"""
import random, sys
from pathlib import Path

LITS = ["", "Zg==", "Zg=", "Zg", "Zm8=", "Zm8", "Zm9v", "Zm9vYg==", "Zm9vYg", "Zm9vYmE=", "Zm9vYmE", "Zm9vYmFy",
        "YWx\0pY2U==", "iYU=", "iYV=", "iYW=", "iYX=", "AAAAiYX=", "/w==", "/x==", "//==", "AAAA/x==",
        "YWxpY2U=====", "YWxpY2UABB====", "YWxpY2UABB=B", "==Y=Wx===pY=2U=====", "EEE===", "EE====", "E=", "E==",
        "E", "ABCDE", "====", "=====", "ABCD=E", "ABCD==E", "A A=", "AB\tC", "aGVsbG8gd29ybGQ=", "Zm9vYmFyYmF6cXV4",
        "Zm9vYmFyYmF6cXV4cXV1eGNvcmdlZ3JhdWx0Z2FycGx5eg==", "aGVsbG8gaW50ZXJuZXR-Cg==", "aGVsbG8gaW50ZXJuZXR+Cg==",
        "ABCDABCDABCDZg=", "ABCDABCDABCDABCDABCDABCDABCDABCDABCDZm8", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.AAA",
        "QUJD\nREVG", "ZZ==", "ZZZ="]
SIZES = {"S": (300, (0, 100)), "M": (500, (300, 700)), "L": (500, (3000, 7000))}


def enc_len(n, pad):
    return (n + 2) // 3 * 4 if pad else n // 3 * 4 + [0, 2, 3][n % 3]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191025 + i)
        n, (lo, hi) = SIZES[size]
        lines = []
        if size == "S":
            for s in LITS:
                for cs in "SUC":
                    for allow in "01":
                        lines.append("lit\t%s\t%s\t%s" % (cs, allow, s.encode("latin-1").hex()))
        for _ in range(n):
            cs = rng.choice("SUC")
            allow = rng.choice("0001")
            pad = rng.choice("01")
            raw = rng.randint(lo, hi)
            el = enc_len(raw, pad == "1")
            r = rng.random()
            if r < 0.85 or el == 0:
                mut = "none"
            elif r < 0.93:
                # invalid or out-of-alphabet byte somewhere, biased toward the tail
                pos = rng.choice([rng.randrange(el), max(0, el - 1 - rng.randrange(min(el, 10)))])
                mut = "set:%d:%d" % (pos, rng.choice([0x3D, 0x20, 0x0A, 0x2E, 0x2B, 0x2D, 0x5F, 0x00, 0xC3, 0x41]))
            else:
                mut = "cut:%d" % rng.randint(1, min(el, 3))
            lines.append("gen\t%s\t%s\t%s\t%d\t%d\t%s" % (cs, allow, pad, raw, rng.randrange(1, 2**63), mut))
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")
