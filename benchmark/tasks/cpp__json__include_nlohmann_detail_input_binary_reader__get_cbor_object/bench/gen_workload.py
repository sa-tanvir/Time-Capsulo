"""Seeded workload generator for binary_reader::get_cbor_object. Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <input bytes as hex> TAB <declared member count, -1 = indefinite> TAB <limit>.
The first byte is the map's initial byte, already consumed by the driver; the count is passed to get_cbor_object as the argument.
limit = -1: the recording SAX handler accepts every event; limit = n >= 0: the (n+1)-th event and every later one is refused (returns false).
S: hand-written valid and invalid maps (nested, indefinite, non-string keys, truncations, refused events) plus random small maps;
M/L: maps with 800 / 12000 members whose values are random small CBOR trees.
"""
import random, struct, sys, types
from pathlib import Path

LIBSRC = 'import struct\n\n\ndef head(major, n, wide=0):\n    """CBOR initial byte(s) for `major` and argument n; wide>0 forces a longer (non-minimal) encoding."""\n    m = major << 5\n    if n < 24 and wide == 0:\n        return bytes([m | n])\n    if n < 256 and wide <= 1:\n        return bytes([m | 24, n])\n    if n < 65536 and wide <= 2:\n        return bytes([m | 25]) + struct.pack(">H", n)\n    if n < 2 ** 32 and wide <= 3:\n        return bytes([m | 26]) + struct.pack(">I", n)\n    return bytes([m | 27]) + struct.pack(">Q", n)\n\n\ndef enc_str(s, rng, indef=0.0, wide=0.0):\n    b = s.encode("utf-8")\n    if rng.random() < indef:\n        out = b"\\x7f"\n        i = 0\n        while i < len(b):\n            k = rng.randrange(1, 40)\n            chunk = b[i:i + k]\n            out += head(3, len(chunk)) + chunk\n            i += k\n        return out + b"\\xff"\n    w = rng.randrange(1, 5) if rng.random() < wide else 0\n    return head(3, len(b), w) + b\n\n\ndef enc(v, rng, indef=0.1, wide=0.1):\n    if v is None: return b"\\xf6"\n    if v is True: return b"\\xf5"\n    if v is False: return b"\\xf4"\n    if isinstance(v, int):\n        w = rng.randrange(1, 5) if rng.random() < wide else 0\n        return head(0, v, w) if v >= 0 else head(1, -1 - v, w)\n    if isinstance(v, float):\n        f32 = struct.unpack(">f", struct.pack(">f", v))[0]\n        if f32 == v:\n            return b"\\xfa" + struct.pack(">f", v)\n        return b"\\xfb" + struct.pack(">d", v)\n    if isinstance(v, str):\n        return enc_str(v, rng, indef, wide)\n    if isinstance(v, list):\n        if rng.random() < indef:\n            return b"\\x9f" + b"".join(enc(x, rng, indef, wide) for x in v) + b"\\xff"\n        w = rng.randrange(1, 5) if rng.random() < wide else 0\n        return head(4, len(v), w) + b"".join(enc(x, rng, indef, wide) for x in v)\n    if isinstance(v, dict):\n        return enc_map(v, rng, indef, wide)[0]\n    raise TypeError(v)\n\n\ndef enc_map(d, rng, indef=0.1, wide=0.1, force_indef=None):\n    """returns (bytes, declared member count or -1 for an indefinite map)"""\n    items = b"".join(enc_str(k, rng, indef, wide) + enc(x, rng, indef, wide) for k, x in d.items())\n    ind = (rng.random() < indef) if force_indef is None else force_indef\n    if ind:\n        return b"\\xbf" + items + b"\\xff", -1\n    return head(5, len(d)) + items, len(d)\n\n\nWORDS = ["alpha", "beta", "gamma", "delta", "id", "name", "value", "k", "x", "y", "z", "list", "data", "eé", "€", "", "a b", "long" * 10]\n\n\ndef scalar(rng):\n    t = rng.randrange(8)\n    if t == 0: return None\n    if t == 1: return rng.random() < 0.5\n    if t == 2: return rng.randrange(0, 24)\n    if t == 3: return rng.choice([rng.randrange(24, 300), rng.randrange(300, 70000), rng.randrange(70000, 2 ** 33), rng.randrange(2 ** 33, 2 ** 63)])\n    if t == 4: return -1 - rng.choice([rng.randrange(0, 24), rng.randrange(24, 300), rng.randrange(300, 70000), rng.randrange(70000, 2 ** 40)])\n    if t == 5: return rng.randrange(-2000, 2000) / 8.0\n    if t == 6: return rng.randrange(-10 ** 6, 10 ** 6) / 1000.0\n    return "".join(rng.choice("abcdefghij é€") for _ in range(rng.randrange(0, 12)))\n\n\ndef gen(rng, depth, budget):\n    if depth == 0 or budget <= 1 or rng.random() < 0.55:\n        return scalar(rng)\n    n = rng.randrange(0, 6)\n    share = max(1, budget // max(n, 1))\n    if rng.random() < 0.5:\n        return [gen(rng, depth - 1, share) for _ in range(n)]\n    return {rng.choice(WORDS) + str(i): gen(rng, depth - 1, share) for i in range(n)}\n'
cbor = types.ModuleType("cbor")
exec(LIBSRC, cbor.__dict__)


def member_count_hex(rng, d, force=None):
    b, n = cbor.enc_map(d, rng, indef=0.15, wide=0.1, force_indef=force)
    if n > 0:   # the driver consumes exactly one initial byte: shorten wide headers to one placeholder byte
        b = b[:1] + b[len(cbor.head(5, n)):]
    return b.hex(), n


def rnd_map(rng, n, depth, budget):
    return {cbor.WORDS[rng.randrange(len(cbor.WORDS))] + str(i): cbor.gen(rng, depth, budget) for i in range(n)}


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for size in "SML":
        rng = random.Random(20191111 + "SML".index(size))
        lines = []
        if size == "S":
            raw = [("a0", 0), ("bf" + "ff", -1), ("a1" + "6161" + "01", 1), ("a2" + "6161" + "01" + "6162" + "02", 2), ("bf" + "6161" + "01" + "ff", -1),
                   ("a1" + "6161" + "a1" + "6162" + "f5", 1), ("a1" + "6161" + "9f0102ff", 1), ("a2" + "6161" + "01", 2), ("a1" + "6161", 1), ("a1" + "61", 1), ("a1", 1),
                   ("a1" + "01" + "02", 1), ("a1" + "40" + "01", 1), ("bf" + "01" + "02" + "ff", -1), ("bf" + "6161" + "01", -1), ("bf", -1), ("a1" + "7f6162ff" + "f6", 1),
                   ("a2" + "6161" + "f4" + "6162", 2), ("a1" + "6161" + "5f", 1), ("a1" + "6161" + "c0", 1), ("a1" + "6161" + "62c3a9", 1), ("a3" + "60" + "00" + "6161" + "20" + "62c3a9" + "fa3fc00000", 3),
                   ("a1" + "6161" + "fb3ff8000000000000", 1), ("a1" + "6161" + "f93c00", 1), ("a1" + "6161" + "1801", 1), ("a1" + "6161" + "3903e7", 1), ("a1" + "6161" + "1b00000001000000" + "00", 1),
                   ("a1" + "6161" + "01" + "ff", 1), ("a0" + "61", 0), ("a2" + "6161" + "01" + "6161" + "02", 2), ("a1" + "6161" + "a0", 1), ("a1" + "6161" + "bfff", 1),
                   ("a1" + "6161" + "a1" + "6162", 1)]
            for h, n in raw:
                lines.append("\t".join(["1", h, str(n), "-1"]))
            for lim in (0, 1, 2, 3, 5):
                lines.append("\t".join(["1", "a2" + "6161" + "01" + "6162" + "9f0102ff", "2", str(lim)]))
                lines.append("\t".join(["1", "bf" + "6161" + "a1" + "6162" + "f5" + "ff", "-1", str(lim)]))
            for _ in range(24):
                d = rnd_map(rng, rng.randrange(0, 5), 3, 20)
                h, n = member_count_hex(rng, d)
                if rng.random() < 0.25:
                    h = h[:2 * rng.randrange(1, len(h) // 2 + 1)]
                lines.append("\t".join(["1", h, str(n), "-1" if rng.random() < 0.85 else str(rng.randrange(0, 8))]))
        else:
            ncase, nmem, depth, budget, reps = {"M": (6, 800, 2, 6, 6), "L": (5, 12000, 2, 6, 1)}[size]
            for c in range(ncase):
                d = rnd_map(rng, nmem, depth, budget)
                h, n = member_count_hex(rng, d, force=(c % 3 == 2))
                lines.append("\t".join([str(reps), h, str(n), "-1"]))
        (out / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")


main()
