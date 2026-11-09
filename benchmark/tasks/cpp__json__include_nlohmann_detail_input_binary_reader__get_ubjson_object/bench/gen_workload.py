"""Seeded workload generator for binary_reader::get_ubjson_object. Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <input bytes as hex> TAB 0 TAB <limit>.
The first byte of the input is '{', already consumed by the driver; get_ubjson_object reads the rest.
limit = -1: the recording SAX handler accepts every event; limit = n >= 0: the (n+1)-th event and every later one is refused (returns false).
S: hand-written valid and invalid UBJSON objects (plain, counted, typed+counted, no-op bytes, every number/string marker, nested containers, truncations)
plus random objects, optionally truncated or followed by trailing bytes; M/L: objects with 800 / 12000 members whose values are random UBJSON trees.
"""
import random, struct, sys, types
from pathlib import Path

LIBSRC = 'import struct\n\nINT_FMT = {"i": ">b", "U": ">B", "I": ">h", "l": ">i", "L": ">q"}\nINT_RANGE = {"i": (-128, 127), "U": (0, 255), "I": (-32768, 32767), "l": (-2 ** 31, 2 ** 31 - 1), "L": (-2 ** 63, 2 ** 63 - 1)}\nORDER = ["i", "U", "I", "l", "L"]\n\n\ndef int_marker(v, rng=None, wide=0.0):\n    ok = [m for m in ORDER if INT_RANGE[m][0] <= v <= INT_RANGE[m][1]]\n    if rng is not None and rng.random() < wide:\n        return rng.choice(ok)\n    # smallest\n    return ok[0] if ok[0] != "U" or v > 127 else ok[0]\n\n\ndef enc_int(v, rng=None, wide=0.0):\n    m = int_marker(v, rng, wide)\n    return m.encode() + struct.pack(INT_FMT[m], v)\n\n\ndef enc_len(n, rng=None, wide=0.0):\n    m = int_marker(n, rng, wide)\n    return m.encode() + struct.pack(INT_FMT[m], n)\n\n\ndef kind(v):\n    if v is None: return "Z"\n    if v is True: return "T"\n    if v is False: return "F"\n    if isinstance(v, int): return "int"\n    if isinstance(v, float): return "D"\n    if isinstance(v, str): return "S"\n    if isinstance(v, list): return "["\n    return "{"\n\n\ndef common_type(vals):\n    ks = set(kind(x) for x in vals)\n    if len(ks) != 1 or not vals:\n        return None\n    k = ks.pop()\n    if k == "int":\n        for m in ORDER:\n            if all(INT_RANGE[m][0] <= x <= INT_RANGE[m][1] for x in vals):\n                return m\n        return None\n    if k == "S" and any(len(x) == 1 for x in vals):\n        pass\n    return k\n\n\ndef payload(v, t, rng, cfg):\n    """encoding of v for a value whose type marker t is known (no marker byte)"""\n    if t in INT_FMT: return struct.pack(INT_FMT[t], v)\n    if t == "D": return struct.pack(">d", v)\n    if t == "d": return struct.pack(">f", v)\n    if t == "S": return enc_len(len(v.encode()), rng, cfg["wide"]) + v.encode()\n    if t in "TFZ": return b""\n    if t == "[": return enc_array(v, rng, cfg, marker=False)\n    if t == "{": return enc_object(v, rng, cfg, marker=False)\n    raise ValueError(t)\n\n\ndef noop(rng, cfg):\n    return b"N" if rng.random() < cfg["noop"] else b""\n\n\ndef enc(v, rng, cfg):\n    if v is None: return b"Z"\n    if v is True: return b"T"\n    if v is False: return b"F"\n    if isinstance(v, int):\n        m = int_marker(v, rng, cfg["wide"])\n        return m.encode() + struct.pack(INT_FMT[m], v)\n    if isinstance(v, float):\n        f32 = struct.unpack(">f", struct.pack(">f", v))[0]\n        if f32 == v and rng.random() < 0.7:\n            return b"d" + struct.pack(">f", v)\n        return b"D" + struct.pack(">d", v)\n    if isinstance(v, str):\n        b = v.encode()\n        if len(b) == 1 and b[0] < 128 and rng.random() < 0.6:\n            return b"C" + b\n        return b"S" + enc_len(len(b), rng, cfg["wide"]) + b\n    if isinstance(v, list): return enc_array(v, rng, cfg)\n    return enc_object(v, rng, cfg)\n\n\ndef style(vals, rng, cfg):\n    r = rng.random()\n    t = common_type(vals) if vals else None\n    if t is not None and r < cfg["typed"]:\n        return "typed", t\n    if r < cfg["typed"] + cfg["counted"]:\n        return "counted", None\n    return "plain", None\n\n\ndef enc_array(v, rng, cfg, marker=True):\n    out = b"[" if marker else b""\n    st, t = style(v, rng, cfg)\n    if st == "typed":\n        out += b"$" + t.encode() + b"#" + enc_len(len(v), rng, cfg["wide"]) + b"".join(payload(x, t, rng, cfg) for x in v)\n    elif st == "counted":\n        out += b"#" + enc_len(len(v), rng, cfg["wide"]) + b"".join(noop(rng, cfg) + enc(x, rng, cfg) for x in v)\n    else:\n        out += b"".join(noop(rng, cfg) + enc(x, rng, cfg) for x in v) + noop(rng, cfg) + b"]"\n    return out\n\n\ndef enc_key(k, rng, cfg):\n    b = k.encode()\n    return enc_len(len(b), rng, cfg["wide"]) + b\n\n\ndef enc_object(d, rng, cfg, marker=True):\n    out = b"{" if marker else b""\n    vals = list(d.values())\n    st, t = style(vals, rng, cfg)\n    if st == "typed":\n        out += b"$" + t.encode() + b"#" + enc_len(len(d), rng, cfg["wide"]) + b"".join(enc_key(k, rng, cfg) + payload(x, t, rng, cfg) for k, x in d.items())\n    elif st == "counted":\n        out += b"#" + enc_len(len(d), rng, cfg["wide"]) + b"".join(enc_key(k, rng, cfg) + noop(rng, cfg) + enc(x, rng, cfg) for k, x in d.items())\n    else:\n        out += b"".join(enc_key(k, rng, cfg) + enc(x, rng, cfg) + noop(rng, cfg) for k, x in d.items()) + b"}"\n    return out\n\n\nWORDS = ["alpha", "beta", "gamma", "delta", "id", "name", "value", "k", "x", "y", "z", "list", "data", "eé", "€", "", "a b", "long" * 10]\n\n\ndef scalar(rng):\n    t = rng.randrange(9)\n    if t == 0: return None\n    if t == 1: return rng.random() < 0.5\n    if t == 2: return rng.randrange(-120, 120)\n    if t == 3: return rng.randrange(120, 300)\n    if t == 4: return rng.randrange(300, 70000) * rng.choice([1, -1])\n    if t == 5: return rng.randrange(-2 ** 40, 2 ** 40)\n    if t == 6: return rng.randrange(-2000, 2000) / 8.0\n    if t == 7: return rng.randrange(-10 ** 6, 10 ** 6) / 1000.0\n    return "".join(rng.choice("abcdefghij é€") for _ in range(rng.choice([0, 1, 1, 2, 5, 11])))\n\n\ndef homogeneous(rng):\n    """a list of same-typed scalars (eligible for typed containers)"""\n    n = rng.randrange(0, 12)\n    t = rng.randrange(6)\n    if t == 0: return [rng.randrange(-100, 100) for _ in range(n)]\n    if t == 1: return [rng.randrange(0, 255) for _ in range(n)]\n    if t == 2: return [rng.randrange(-30000, 30000) for _ in range(n)]\n    if t == 3: return [True] * n\n    if t == 4: return ["w" + str(rng.randrange(100)) for _ in range(n)]\n    return [rng.randrange(-1000, 1000) / 4.0 for _ in range(n)]\n\n\ndef gen(rng, depth, budget):\n    if depth == 0 or budget <= 1 or rng.random() < 0.5:\n        return scalar(rng)\n    r = rng.random()\n    if r < 0.25:\n        return homogeneous(rng)\n    n = rng.randrange(0, 6)\n    share = max(1, budget // max(n, 1))\n    if r < 0.6:\n        return [gen(rng, depth - 1, share) for _ in range(n)]\n    return {rng.choice(WORDS) + str(i): gen(rng, depth - 1, share) for i in range(n)}\n\n\nCFG = {"typed": 0.3, "counted": 0.3, "wide": 0.1, "noop": 0.03}\n'
ubj = types.ModuleType("ubj")
exec(LIBSRC, ubj.__dict__)


def enc_top(v, rng):
    return ubj.enc_object(v, rng, ubj.CFG)


def top_obj(rng, depth, budget):
    n = rng.randrange(0, 6)
    return {ubj.WORDS[rng.randrange(len(ubj.WORDS))] + str(i): ubj.gen(rng, depth, budget) for i in range(n)}


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for size in "SML":
        rng = random.Random(20191111 + "SML".index(size))
        lines = []
        if size == "S":
            raw = [x.hex() for x in [b"{}", b"{i\x01ai\x01}", b"{i\x01ai\x01i\x01bi\x02}", b"{#i\x02i\x01ai\x01i\x01bi\x02", b"{#U\x01i\x01aSi\x03abc", b"{#I\x00\x01i\x01aZ", b"{#l\x00\x00\x00\x01i\x01aT", b"{#L\x00\x00\x00\x00\x00\x00\x00\x00",
       b"{#i\x00", b"{$i#i\x02i\x01a\x01i\x01b\x02", b"{$U#i\x02i\x01a\xc8i\x01b\x05", b"{$S#i\x02i\x01ai\x02hii\x01bi\x01x", b"{$T#i\x02i\x01ai\x01b", b"{$Z#i\x01i\x01a",
       b"{$[#i\x02i\x01ai\x01]i\x01b]", b"{${#i\x01i\x01ai\x01ci\x01}", b"{$d#i\x01i\x01a?\x80\x00\x00", b"{$D#i\x01i\x01a@\x09\x21\xfb\x54\x44\x2d\x18", b"{$C#i\x01i\x01ax",
       b"{i\x01a[i\x01i\x02]i\x01b{i\x01ci\x03}}", b"{i\x01aSi\x03abci\x01bCx}", b"{i\x01aU\xffi\x01bI\x01\x00i\x01cl\x00\x01\x00\x00i\x01dL\x00\x00\x00\x01\x00\x00\x00\x00i\x01ed?\x80\x00\x00i\x01fD@\x09\x21\xfb\x54\x44\x2d\x18i\x01gZi\x01hTi\x01iF}",
       b"{Ni\x01aNi\x01Ni\x01bZN}", b"{#i\x02i\x01aNi\x01i\x01bNi\x02", b"{U\x01ai\x01}", b"{I\x00\x01ai\x01}", b"{i\x00i\x01}", b"{i\x01ai\x01i\x01a i\x02}",
       b"{", b"{i", b"{i\x01", b"{i\x01a", b"{i\x01ai", b"{i\x01ai\x01", b"{A", b"{i\x01aA}", b"{i\x01a[i\x01", b"{$", b"{$i", b"{$ix", b"{$i#", b"{$i#A", b"{#", b"{#A", b"{#i", b"{#i\x02i\x01ai\x01",
       b"{$N#i\x01i\x01a", b"{$N#i\x00", b"{#i\x01i\x01aC\xff", b"{i\x01aC\xff}", b"{$C#i\x01i\x01a\xe9", b"{$i#i\x02i\x01a\x01", b"{$#i\x01", b"{$i#i\x01i", b"{$i#i\x01i\x01", b"{$S#i\x01i\x01aU", b"{$[#i\x01i\x01ai\x01", b"{#i\x03i\x01aZi\x01bZ",
       b"{#L\x00\x00\x01\x00\x00\x00\x00\x00i\x01aZ"]]
            for h in raw:
                lines.append("\t".join(["1", h, "0", "-1"]))
            for lim in (0, 1, 2, 3, 4, 6):
                for h in [x.hex() for x in [b"{i\x01ai\x01i\x01b[i\x02]}", b"{#i\x02i\x01aTi\x01b{i\x01cF}", b"{$i#i\x03i\x01a\x01i\x01b\x02i\x01c\x03"]]:
                    lines.append("\t".join(["1", h, "0", str(lim)]))
            for _ in range(40):
                v = top_obj(rng, 3, 20)
                b = enc_top(v, rng)
                r = rng.random()
                if r < 0.2 and len(b) > 1:
                    b = b[:rng.randrange(1, len(b))]
                elif r < 0.3:
                    b += b"\x00ZZ"
                lines.append("\t".join(["1", b.hex(), "0", "-1" if rng.random() < 0.85 else str(rng.randrange(0, 8))]))
        else:
            ncase, nmem, depth, budget, reps = {"M": (6, 800, 2, 6, 6), "L": (5, 12000, 2, 6, 1)}[size]
            for c in range(ncase):
                v = {ubj.WORDS[rng.randrange(len(ubj.WORDS))] + str(i): ubj.gen(rng, depth, budget) for i in range(nmem)}
                b = enc_top(v, rng)
                lines.append("\t".join([str(reps), b.hex(), "0", "-1"]))
        (out / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")


main()
