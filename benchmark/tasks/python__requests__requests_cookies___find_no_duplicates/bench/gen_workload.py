"""Seeded workload generator for RequestsCookieJar._find_no_duplicates. Usage: python3 gen_workload.py <out_dir>"""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (40, 10), "M": (40, 100), "L": (40, 1000)}   # (jars, cookies per jar)
DOMAINS = ["", "example.com", ".example.com", "api.example.com", "test1.com", "test2.com"]
PATHS = ["/", "/a", "/a/b", "some_path", "/api"]


def ident(rng):
    return "c" + "".join(rng.choice(string.ascii_lowercase + string.digits) for _ in range(rng.randint(1, 6)))


def case(rng, n):
    names = [ident(rng) for _ in range(max(1, n // 2))]
    cookies = []
    for _ in range(n):
        val = rng.choice(["", "v" + ident(rng), '"quoted"', "x" * rng.randint(1, 20)])
        cookies.append([rng.choice(names), val, rng.choice(DOMAINS), rng.choice(PATHS)])
    queries = []
    for _ in range(20):
        nm = rng.choice(names) if rng.random() < 0.85 else ident(rng) + "_missing"
        queries.append([nm, rng.choice([None, None] + DOMAINS), rng.choice([None, None] + PATHS)])
    return {"cookies": cookies, "queries": queries}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, c)) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, c) for _ in range(n)]))
