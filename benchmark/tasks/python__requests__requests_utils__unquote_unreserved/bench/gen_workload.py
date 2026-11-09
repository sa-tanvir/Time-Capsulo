"""Seeded workload generator for unquote_unreserved. Usage: python3 gen_workload.py <out_dir>"""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (300, 60), "M": (300, 600), "L": (300, 6000)}   # (cases, max URI length in tokens)
PLAIN = string.ascii_letters + string.digits + "/:?&=.-_~+!$'()*,;@[]"


def token(rng, bad_ok):
    r = rng.random()
    if r < 0.55:
        return rng.choice(PLAIN)
    if r < 0.92:
        return "%" + "".join(rng.choice("0123456789abcdefABCDEF") for _ in range(2))
    if r < 0.97:
        return "%" + rng.choice(["-", "/", " ", "4-", ".x", "-41"])
    if bad_ok:
        return "%" + rng.choice(["zz", "G1", "pp", "x0", "é1"])
    return "%25"


def case(rng, n):
    bad_ok = rng.random() < 0.1
    s = "http://example.com/" + "".join(token(rng, bad_ok) for _ in range(rng.randint(0, n)))
    if rng.random() < 0.05:
        s += "%"
    return s


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, c)) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, c) for _ in range(n)], ensure_ascii=False))
