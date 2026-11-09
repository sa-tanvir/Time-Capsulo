"""Seeded workload generator for OptionParser._match_long_opt. Usage: python3 gen_workload.py <out_dir>

Each case is one parser plus a sequence of long-option tokens matched against one parsing state.
Per-case scale grows ~10x per size: registered options / remaining args / tokens per case are
about 10/24/8 (S), 100/240/80 (M), 1000/2400/800 (L)."""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (10, 60), "M": (100, 60), "L": (1000, 60)}   # (scale, cases)
PREFIXES = ["--", "--", "--", "-", "+", "/", "++"]
ACTIONS = ["store", "store", "store", "append", "store_const", "append_const", "count"]


def word(rng):
    return "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(2, 9)))


def case(rng, scale):
    opts, seen = [], set()
    while len(opts) < scale:
        name = rng.choice(PREFIXES) + word(rng)
        if name in seen:
            continue
        seen.add(name)
        action = rng.choice(ACTIONS)
        nargs = rng.choice([1, 1, 1, 2, 3]) if action in ("store", "append") else 1
        opts.append([name, "d%d" % len(opts), action, nargs])
    rargs = [rng.choice([word(rng), "-x", "--", "", str(rng.randint(0, 99))]) for _ in range(int(scale * 2.4))]
    calls = []
    for _ in range(max(1, int(scale * 0.8))):
        r = rng.random()
        name = rng.choice(opts)[0]
        if r < 0.03:
            name = name[:rng.randint(1, len(name))]          # prefix of a known option
        elif r < 0.05:
            name = rng.choice(["--", "-"]) + word(rng)       # unknown
        elif r < 0.06:
            name = name.upper()
        ev = None
        if rng.random() < 0.08:
            ev = rng.choice(["", "v", word(rng), "a=b"])
        calls.append([name, ev])
    return {"ctx": rng.random() < 0.5, "opts": opts, "rargs": rargs, "calls": calls}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (scale, n)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        data = {"cases": [case(rng, scale) for _ in range(n)]}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(data))
