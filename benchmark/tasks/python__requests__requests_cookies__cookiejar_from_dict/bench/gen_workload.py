"""Seeded workload generator for cookiejar_from_dict. Usage: python3 gen_workload.py <out_dir>"""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (60, 10), "M": (60, 100), "L": (60, 1000)}   # (cases, max cookies in dict / jar)
DOMAINS = ["", "example.com", ".example.com", "api.example.com"]
PATHS = ["/", "/a", "/api"]


def ident(rng):
    return "k" + "".join(rng.choice(string.ascii_lowercase + string.digits) for _ in range(rng.randint(1, 4)))


def case(rng, n):
    pool = [ident(rng) for _ in range(max(2, n))]
    d = {}
    if rng.random() < 0.05:
        d = None
    else:
        for _ in range(rng.randint(0, n)):
            d[rng.choice(pool)] = rng.choice(["v" + ident(rng), "", '"q\\"x"', "0"])
    jar_kind = rng.choice(["none", "requests", "requests", "plain"])
    jar = []
    if jar_kind != "none":
        for _ in range(rng.randint(0, n)):
            jar.append([rng.choice(pool), "j" + ident(rng), rng.choice(DOMAINS), rng.choice(PATHS)])
    return {"dict": d, "jar_kind": jar_kind, "jar": jar, "overwrite": rng.choice([True, False, None])}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, c)) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, c) for _ in range(n)]))
