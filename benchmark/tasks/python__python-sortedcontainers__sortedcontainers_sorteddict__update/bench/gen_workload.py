"""Seeded workload generator for SortedDict.update. Usage: python3 gen_workload.py <out_dir>

Cases are recipes (seed + sizes); the driver expands them deterministically, so files stay tiny."""
import json, random, sys
from pathlib import Path

SIZES = {"S": (40, 1_000), "M": (24, 10_000), "L": (16, 100_000)}   # (cases, max base size)
FORMS = ["dict", "pairs", "pairs", "kwargs", "mixed", "sorteddict", "none"]


def cases(n_cases, max_n, rng):
    out = []
    for i in range(n_cases):
        n_base = 0 if i % 8 == 0 else rng.randint(max_n // 4, max_n)
        ratio = rng.choice([0.0005, 0.005, 0.02, 0.05, 0.09, 0.12, 0.3, 1.0, 2.0])
        n_upd = max(1, int(max(n_base, max_n // 10) * ratio))
        form = rng.choice(FORMS)
        str_keys = form in ("kwargs", "mixed") or rng.random() < 0.2
        out.append({
            "seed": rng.randint(0, 2**31),
            "n_base": n_base,
            "n_upd": n_upd,
            "keyspace": rng.choice([2, 4]) * max(n_base, n_upd),
            "form": form,
            "str_keys": str_keys,
            "key_fn": None if str_keys else rng.choice([None, None, "neg"]),
        })
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m)) in enumerate(SIZES.items()):
        rng = random.Random(20181122 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, m, rng)))
