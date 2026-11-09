"""Seeded workload generator for OptionParser._match_short_opt. Usage: python3 gen_workload.py <out_dir>

Each case is one parser plus 5 short-option cluster tokens matched against one parsing state.
Per-case scale grows ~10x per size: cluster tokens are up to ~8 (S), 80 (M), 800 (L) characters long."""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (8, 100), "M": (80, 100), "L": (800, 100)}   # (max token length, cases)
ACTIONS = ["store_const", "append_const", "count", "count", "store_const", "store", "append"]


def case(rng, scale):
    prefix = rng.choice(["-", "-", "-", "+", "/"])
    letters = rng.sample(string.ascii_lowercase + string.digits, 30)
    opts = []
    for k, ch in enumerate(letters):
        action = rng.choice(ACTIONS)
        nargs = rng.choice([1, 1, 2]) if action in ("store", "append") else 1
        opts.append([prefix + ch, "d%d" % k, action, nargs])
    novalue = [o[0][1] for o in opts if o[2] not in ("store", "append")]
    value = [o[0][1] for o in opts if o[2] in ("store", "append")]
    unknown = [c for c in string.ascii_lowercase + string.digits if c not in letters]
    ignore = rng.random() < 0.5
    lower = rng.random() < 0.3
    tokens = []
    for _ in range(5):
        n = rng.randint(1, scale)
        chars = []
        for _ in range(n):
            r = rng.random()
            if ignore and r < 0.15:
                chars.append(rng.choice(unknown))
            else:
                c = rng.choice(novalue)
                chars.append(c.upper() if lower and c.isalpha() and rng.random() < 0.3 else c)
        r = rng.random()
        if r < 0.4 and value:
            chars.append(rng.choice(value))
            if rng.random() < 0.6:
                chars.extend(rng.choice(string.ascii_letters + "=.-") for _ in range(rng.randint(1, scale)))
        elif r < 0.43 and not ignore:
            chars.insert(rng.randrange(len(chars) + 1), rng.choice(unknown))
        tokens.append(prefix + "".join(chars))
    rargs = [rng.choice(["a", "b.txt", "-x", "--", "", "42"]) for _ in range(rng.randint(0, 8))]
    return {"ctx": lower or rng.random() < 0.3, "lower": lower, "ignore": ignore,
            "opts": opts, "rargs": rargs, "tokens": tokens}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (scale, n)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        data = {"cases": [case(rng, scale) for _ in range(n)]}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(data))
