"""Seeded workload generator for merge_cookies. Usage: python3 gen_workload.py <out_dir>"""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (60, 10), "M": (60, 100), "L": (60, 1000)}   # (cases, max cookies per side)
DOMAINS = ["", "example.com", ".example.com", "api.example.com"]
PATHS = ["/", "/a", "/api"]


def ident(rng):
    return "k" + "".join(rng.choice(string.ascii_lowercase + string.digits) for _ in range(rng.randint(1, 4)))


def cookies(rng, pool, n, default_only=False):
    out = []
    for _ in range(rng.randint(0, n)):
        d, p = ("", "/") if default_only or rng.random() < 0.4 else (rng.choice(DOMAINS), rng.choice(PATHS))
        out.append([rng.choice(pool), "v" + ident(rng), d, p])
    return out


def case(rng, n):
    pool = [ident(rng) for _ in range(max(2, n))]
    target_kind = rng.choice(["requests"] * 5 + ["plain"] * 3 + ["notajar"])
    src_kind = rng.choice(["dict", "dict", "requests", "requests", "plain", "none"])
    return {"target_kind": target_kind, "target": cookies(rng, pool, n),
            "src_kind": src_kind, "src": cookies(rng, pool, n)}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, c)) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, c) for _ in range(n)]))
