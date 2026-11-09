"""Seeded workload generator for numeric_range(). Usage: python3 gen_workload.py <out_dir>

Each argument is encoded as [type, payload]: int / float (dyadic, so exact) / frac [num, den] /
dec "string" / dt [seconds offset] / td [seconds]."""
import json, random, sys
from pathlib import Path

SIZES = {"S": (300, 40), "M": (150, 300), "L": (200, 2_000)}   # (cases, max number of items)

def num(rng, kind, x):
    if kind == "int":
        return ["int", int(x)]
    if kind == "float":
        return ["float", float(x)]
    if kind == "frac":
        return ["frac", [int(x * 4), 4]]
    return ["dec", str(x)]

def case(rng, max_items):
    kind = rng.choice(["int", "float", "frac", "dec", "dt", "mixed"])
    items = rng.randint(0, max_items)
    sign = rng.choice([1, 1, -1])
    if kind == "dt":
        step_s = sign * rng.choice([1, 60, 3600, 86400])
        start = rng.randint(0, 10**8)
        stop = start + step_s * items - sign * rng.randint(0, abs(step_s) - 1 if abs(step_s) > 1 else 0)
        return [["dt", start], ["dt", stop], ["td", step_s]]
    if rng.random() < 0.03:
        return [num(rng, "int", 0), num(rng, "int", 5), num(rng, "int", 0)]          # zero step
    if rng.random() < 0.15 and sign > 0 and kind != "mixed":
        return [num(rng, kind, items)]                                             # stop-only form
    step = sign * rng.choice([1, 2, 0.5, 0.25, 3]) if kind in ("float", "frac", "dec", "mixed") \
        else sign * rng.choice([1, 2, 3, 7])
    start = rng.randint(-1000, 1000) / (4 if kind != "int" else 1)
    stop = start + step * items
    if kind == "mixed":
        ks = [rng.choice(["int", "float", "frac"]) for _ in range(3)]
        start, stop = int(start), int(stop)
        return [num(rng, ks[0], start), num(rng, ks[1], stop), num(rng, "float" if step != int(step) else ks[2], step)]
    if step == 1 and rng.random() < 0.3:
        return [num(rng, kind, start), num(rng, kind, stop)]                       # two-arg form
    return [num(rng, kind, start), num(rng, kind, stop), num(rng, kind, step)]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m)) in enumerate(SIZES.items()):
        rng = random.Random(20190720 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, m) for _ in range(n)]))
