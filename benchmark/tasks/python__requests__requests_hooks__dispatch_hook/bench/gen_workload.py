"""Seeded workload generator for requests.hooks.dispatch_hook. Usage: python3 gen_workload.py <out_dir>

Each case: event key, registry shape (None / {} / single callable / list / tuple / empty list), a chain of hook
names (resolved to functions by the driver), initial integer data and optional kwargs. Per-case scale grows ~10x
per size: up to K hooks per chain, K = 4 (S), 40 (M), 400 (L)."""
import json, random, sys
from pathlib import Path

SIZES = {"S": (4, 4000), "M": (40, 2000), "L": (400, 400)}   # (K, cases)
HOOKS = ["inc", "inc", "dbl", "none", "none", "neg", "zero", "half", "step"]


def case(rng, K, allow_raise):
    shape = rng.choices(["none", "empty_dict", "single", "list", "tuple", "empty_list"], [3, 3, 15, 60, 15, 4])[0]
    n = 1 if shape == "single" else (0 if shape == "empty_list" else rng.randint(1, K))
    chain = [rng.choice(HOOKS) for _ in range(n)]
    if allow_raise and chain and rng.random() < 0.03:
        chain[rng.randrange(len(chain))] = "boom"
    return {"key": rng.choice(["response"] * 9 + ["other"]), "shape": shape, "chain": chain,
            "extra": rng.random() < 0.3, "data": rng.randint(-1000, 1000),
            "kwargs": {"step": rng.randint(1, 9)} if rng.random() < 0.5 else {}}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (K, n)) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        cases = [case(rng, K, size == "S") for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
