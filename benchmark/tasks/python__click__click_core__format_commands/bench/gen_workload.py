"""Seeded workload generator for MultiCommand.format_commands. Usage: python3 gen_workload.py <out_dir>

Each case is a multi command: an ordered list of listed names, each either a ghost (unknown name), a hidden
command, or a visible command with optional help / short_help, plus a formatter width.
Per-case scale grows ~10x per size: up to K listed names, K = 8 (S), 80 (M), 800 (L)."""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (8, 400), "M": (80, 60), "L": (800, 40)}   # (K names, cases)
HELPS = [None, "", "This is a short text.", "Login and store the token in ~/.netrc.",
         "This is a long text that is too long to show as short help\n    and will be truncated instead.",
         "SDIST HELP", "Show the version and exit."]


def word(rng, lo=1, hi=10):
    return "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(lo, hi)))


def entry(rng):
    name = "-".join(word(rng, 1, 8) for _ in range(rng.choice([1, 1, 1, 2, 3])))
    kind = rng.choices(["visible", "hidden", "ghost", "hidden_group"], [80, 8, 7, 5])[0]
    e = {"name": name, "kind": kind}
    if kind in ("visible", "hidden"):
        h = rng.choice(HELPS)
        if rng.random() < 0.6:
            h = (h or "") + " " + " ".join(word(rng) for _ in range(rng.randint(0, 30)))
            if rng.random() < 0.5:
                h += "."
        e["help"] = h
        e["short_help"] = rng.choice([None] * 5 + ["Short.", "explicit short help " + word(rng)])
        e["alias"] = rng.random() < 0.1
    return e


def case(rng, K):
    n = rng.randint(0, K)
    entries = [entry(rng) for _ in range(n)]
    if entries and rng.random() < 0.1:
        entries.append(dict(rng.choice(entries)))   # duplicate listed name
    return {"width": rng.choice([20, 40, 60, 78, 80, 80, 100, 120]), "entries": entries}


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (K, n)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        cases = [case(rng, K) for _ in range(n)]
        if size == "S":
            cases = [{"width": 80, "entries": []},
                     {"width": 80, "entries": [{"name": "nope", "kind": "hidden", "help": None, "short_help": None, "alias": False}]},
                     {"width": 80, "entries": [{"name": "subgroup", "kind": "hidden_group"}]},
                     {"width": 80, "entries": [{"name": "ghost", "kind": "ghost"}]},
                     {"width": 80, "entries": [{"name": n, "kind": "visible", "help": h, "short_help": None, "alias": False}
                                               for n, h in (("long", HELPS[4]), ("short", HELPS[2]), ("special-chars", HELPS[3]))]},
                     ] + cases
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
