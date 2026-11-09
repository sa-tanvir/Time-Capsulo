"""Seeded workload generator for binary_reader::get_cbor_string. Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <input bytes as lowercase hex> TAB 0 TAB -1.
The first byte of the input is the one the driver has already read (the string's initial byte); get_cbor_string reads the rest.
S: hand-written valid and invalid CBOR text strings (all length encodings, indefinite and nested indefinite strings, truncations, wrong initial bytes),
plus random strings with random header widths, optional truncation and trailing garbage; M/L: long strings (4 * 10^3 / 3 * 10^5 characters).
"""
import random, struct, sys, types
from pathlib import Path

LIBSRC = 'import struct\n\n\ndef head(major, n, wide=0):\n    """CBOR initial byte(s) for `major` and argument n; wide>0 forces a longer (non-minimal) encoding."""\n    m = major << 5\n    if n < 24 and wide == 0:\n        return bytes([m | n])\n    if n < 256 and wide <= 1:\n        return bytes([m | 24, n])\n    if n < 65536 and wide <= 2:\n        return bytes([m | 25]) + struct.pack(">H", n)\n    if n < 2 ** 32 and wide <= 3:\n        return bytes([m | 26]) + struct.pack(">I", n)\n    return bytes([m | 27]) + struct.pack(">Q", n)\n\n\ndef enc_str(s, rng, indef=0.0, wide=0.0):\n    b = s.encode("utf-8")\n    if rng.random() < indef:\n        out = b"\\x7f"\n        i = 0\n        while i < len(b):\n            k = rng.randrange(1, 40)\n            chunk = b[i:i + k]\n            out += head(3, len(chunk)) + chunk\n            i += k\n        return out + b"\\xff"\n    w = rng.randrange(1, 5) if rng.random() < wide else 0\n    return head(3, len(b), w) + b\n\n\ndef enc(v, rng, indef=0.1, wide=0.1):\n    if v is None: return b"\\xf6"\n    if v is True: return b"\\xf5"\n    if v is False: return b"\\xf4"\n    if isinstance(v, int):\n        w = rng.randrange(1, 5) if rng.random() < wide else 0\n        return head(0, v, w) if v >= 0 else head(1, -1 - v, w)\n    if isinstance(v, float):\n        f32 = struct.unpack(">f", struct.pack(">f", v))[0]\n        if f32 == v:\n            return b"\\xfa" + struct.pack(">f", v)\n        return b"\\xfb" + struct.pack(">d", v)\n    if isinstance(v, str):\n        return enc_str(v, rng, indef, wide)\n    if isinstance(v, list):\n        if rng.random() < indef:\n            return b"\\x9f" + b"".join(enc(x, rng, indef, wide) for x in v) + b"\\xff"\n        w = rng.randrange(1, 5) if rng.random() < wide else 0\n        return head(4, len(v), w) + b"".join(enc(x, rng, indef, wide) for x in v)\n    if isinstance(v, dict):\n        return enc_map(v, rng, indef, wide)[0]\n    raise TypeError(v)\n\n\ndef enc_map(d, rng, indef=0.1, wide=0.1, force_indef=None):\n    """returns (bytes, declared member count or -1 for an indefinite map)"""\n    items = b"".join(enc_str(k, rng, indef, wide) + enc(x, rng, indef, wide) for k, x in d.items())\n    ind = (rng.random() < indef) if force_indef is None else force_indef\n    if ind:\n        return b"\\xbf" + items + b"\\xff", -1\n    return head(5, len(d)) + items, len(d)\n\n\nWORDS = ["alpha", "beta", "gamma", "delta", "id", "name", "value", "k", "x", "y", "z", "list", "data", "eé", "€", "", "a b", "long" * 10]\n\n\ndef scalar(rng):\n    t = rng.randrange(8)\n    if t == 0: return None\n    if t == 1: return rng.random() < 0.5\n    if t == 2: return rng.randrange(0, 24)\n    if t == 3: return rng.choice([rng.randrange(24, 300), rng.randrange(300, 70000), rng.randrange(70000, 2 ** 33), rng.randrange(2 ** 33, 2 ** 63)])\n    if t == 4: return -1 - rng.choice([rng.randrange(0, 24), rng.randrange(24, 300), rng.randrange(300, 70000), rng.randrange(70000, 2 ** 40)])\n    if t == 5: return rng.randrange(-2000, 2000) / 8.0\n    if t == 6: return rng.randrange(-10 ** 6, 10 ** 6) / 1000.0\n    return "".join(rng.choice("abcdefghij é€") for _ in range(rng.randrange(0, 12)))\n\n\ndef gen(rng, depth, budget):\n    if depth == 0 or budget <= 1 or rng.random() < 0.55:\n        return scalar(rng)\n    n = rng.randrange(0, 6)\n    share = max(1, budget // max(n, 1))\n    if rng.random() < 0.5:\n        return [gen(rng, depth - 1, share) for _ in range(n)]\n    return {rng.choice(WORDS) + str(i): gen(rng, depth - 1, share) for i in range(n)}\n'
cbor = types.ModuleType("cbor")
exec(LIBSRC, cbor.__dict__)


def rnd_text(rng, n):
    alpha = "abcdefghijklmnopqrstuvwxyz ABCDEF0123456789é€"
    return "".join(rng.choice(alpha) for _ in range(n))


def trunc(rng, b):
    return b[:rng.randrange(0, len(b))] if len(b) > 1 else b


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for size in "SML":
        rng = random.Random(20191111 + "SML".index(size))
        lines = []
        if size == "S":
            hexes = ["", "60", "61", "6161", "62", "626162", "64" + "41424344", "77" + "61" * 23, "7761", "78" + "00", "7818" + "62" * 24, "78ff" + "63" * 255,
                     "7900" + "00", "790100" + "64" * 256, "7a00000003" + "616263", "7b0000000000000002" + "6162", "7800", "7801", "79", "7901", "7a000000", "7b00000000",
                     "7f" + "ff", "7f" + "6161" + "62" + "6263" + "ff", "7f" + "7f" + "6161" + "ff" + "626263" + "ff", "7f7f7f6161ffffff", "7f", "7f61", "7f6161", "7f6161ff",
                     "7f4161ff", "7f6161ff616262", "7f7861", "7f6161" + "ff" + "ff", "6161ffff", "7f6161" + "6262" + "ff61", "00", "20", "40", "41" + "61", "5f", "80", "a0", "c0",
                     "e0", "f4", "f6", "fa", "ff", "7c", "7d", "7e", "6f" + "61" * 15, "6f" + "61" * 14, "7a00000000", "7b0000000000000000", "7f" + "ff" + "00", "7f6162" + "7f" + "6161" + "ff" + "ff",
                     "7f" + "78" + "02" + "6162" + "ff", "62c3a9", "63e282ac", "7f62c3a962e282ff"]
            for h in hexes:
                lines.append("\t".join(["1", h, "0", "-1"]))
            for _ in range(24):
                s = rnd_text(rng, rng.choice([0, 1, 5, 23, 24, 30, 255, 256, 300]))
                b = cbor.enc_str(s, rng, indef=0.4, wide=0.4)
                r = rng.random()
                if r < 0.2: b = trunc(rng, b)
                elif r < 0.5: b += bytes(rng.randrange(256) for _ in range(rng.randrange(1, 4)))
                lines.append("\t".join(["1", b.hex(), "0", "-1"]))
        else:
            ncase, maxlen, reps = {"M": (24, 4000, 20), "L": (10, 300000, 1)}[size]
            for c in range(ncase):
                n = rng.randrange(maxlen // 10, maxlen)
                s = rnd_text(rng, n)
                b = cbor.enc_str(s, rng, indef=0.5 if c % 2 else 0.0, wide=0.3)
                if c % 7 == 3: b = trunc(rng, b)
                lines.append("\t".join([str(reps), b.hex(), "0", "-1"]))
        (out / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")


main()
