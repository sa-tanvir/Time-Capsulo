"""Seeded workload generator for RequestEncodingMixin._encode_files. Usage: python3 gen_workload.py <out_dir>"""
import json, random, string, sys
from pathlib import Path

# (cases, max data fields, max files, max file bytes)
SIZES = {"S": (60, 4, 3, 400), "M": (60, 40, 10, 4000), "L": (60, 400, 30, 40000)}
CHARS = string.ascii_letters + string.digits + " _.-\"'äöüø€"


def text(rng, lo=1, hi=10):
    return "".join(rng.choice(CHARS) for _ in range(rng.randint(lo, hi)))


def dval(rng):
    r = rng.random()
    if r < 0.5:
        return {"s": text(rng, 0, 30)}
    if r < 0.65:
        return {"b": text(rng, 0, 30)}
    if r < 0.8:
        return {"i": rng.randint(-999, 99999)}
    if r < 0.88:
        return None
    return {"list": [rng.choice([{"s": text(rng)}, {"i": rng.randint(0, 9)}, None]) for _ in range(rng.randint(0, 4))]}


def fobj(rng, maxb):
    n = rng.randint(0, maxb)
    kind = rng.choice(["bytes", "bytes", "str", "bytearray", "stream", "stream", "named_stream", "int", "none"])
    return {"kind": kind, "len": n, "seed": rng.randint(0, 10**6), "name": text(rng) + ".bin"}


def fentry(rng, maxb):
    shape = rng.choice([1, 2, 2, 3, 4])
    fo = fobj(rng, maxb)
    if shape == 1:
        return {"shape": 1, "f": fo}
    return {"shape": shape, "fn": rng.choice([text(rng) + ".txt", None]), "f": fo,
            "ct": rng.choice(["text/plain", "application/octet-stream", None]),
            "hdr": {"X-Part": text(rng, 1, 6)} if shape == 4 else None}


def case(rng, maxd, maxf, maxb):
    r = rng.random()
    if r < 0.03:
        return {"err": "nofiles"}
    if r < 0.06:
        return {"err": "strdata"}
    data = [[{"b": text(rng, 1, 8)} if rng.random() < 0.15 else {"s": text(rng, 1, 8)}, dval(rng)]
            for _ in range(rng.randint(0, maxd))]
    files = [[text(rng, 1, 8), fentry(rng, maxb)] for _ in range(rng.randint(1, maxf))]
    return {"data": data, "data_kind": rng.choice(["dict", "pairs", "none"]) if data else "none",
            "files": files, "files_kind": rng.choice(["dict", "pairs"])}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, cfg) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, *cfg[1:]) for _ in range(cfg[0])]))
