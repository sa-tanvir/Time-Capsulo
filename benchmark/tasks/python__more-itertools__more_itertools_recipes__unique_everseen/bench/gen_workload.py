"""Seeded workload generator for unique_everseen(). Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, max length, max length for unhashable-list cases)
SIZES = {"S": (40, 400, 60), "M": (60, 6_000, 300), "L": (60, 60_000, 800)}

def case(rng, max_len, max_unhash):
    kind = rng.choice(["int", "int", "str", "str_lower", "list", "list_tuple", "mixed", "int_mod"])
    length = rng.randint(0, max_unhash if kind in ("list", "mixed") else max_len)
    distinct = max(1, int(length * rng.choice([0.01, 0.1, 0.5, 1.0])))
    if kind in ("int", "int_mod"):
        data = [rng.randint(0, distinct) for _ in range(length)]
    elif kind in ("str", "str_lower"):
        alpha = "abcdeABCDE"
        data = ["".join(rng.choice(alpha) for _ in range(rng.randint(1, 3))) for _ in range(length)]
    elif kind in ("list", "list_tuple"):
        data = [[rng.randint(0, 3) for _ in range(rng.randint(0, 2))] + [rng.randint(0, distinct)] for _ in range(length)]
    else:
        data = [rng.choice([rng.randint(0, 20), [rng.randint(0, 20)], str(rng.randint(0, 20))]) for _ in range(length)]
    key = {"str_lower": "lower", "list_tuple": "tuple", "int_mod": "mod"}.get(kind)
    return {"data": data, "key": key}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m, u)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, m, u) for _ in range(n)]))
