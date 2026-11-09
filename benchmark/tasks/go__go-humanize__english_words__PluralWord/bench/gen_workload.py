"""Seeded workload generator for english.PluralWord. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, min word length, max word length): per-case word length grows ~10x per size
SIZES = {"S": (6_000, 1, 12), "M": (6_000, 12, 120), "L": (6_000, 120, 1_200)}
EDGE = [[1, "object", ""], [0, "object", ""], [-1, "object", ""], [42, "object", ""], [2, "vax", "vaxen"],
        [1, "vax", "vaxen"], [2, "index", ""], [2, "Index", ""], [2, "matrix", ""], [2, "vertex", ""],
        [2, "bus", ""], [2, "bush", ""], [2, "watch", ""], [2, "church", ""], [2, "box", ""], [2, "BOX", ""],
        [2, "hero", ""], [2, "HERO", ""], [2, "radio", ""], [2, "zoo", ""], [2, "lady", ""], [2, "day", ""],
        [2, "toy", ""], [2, "bAy", ""], [2, "", ""], [2, "o", ""], [2, "y", ""], [2, "s", ""], [2, "x", ""],
        [2, "néo", ""], [1, "", "x"], [3, "index", "indexes"]]
ENDINGS = ["s", "sh", "tch", "ch", "x", "o", "y", "ay", "ey", "oy", "ao", "eo", "Y", "O", "X", "e", "t", "n", "ss"]
LETTERS = "abcdefghijklmnopqrstuvwxyzAEIOU"

def word(rng, lo, hi):
    end = rng.choice(ENDINGS)
    n = max(0, rng.randint(lo, hi) - len(end))
    return "".join(rng.choice(LETTERS) for _ in range(n)) + end

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20180713 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            q = rng.choice([0, 1, 2, 2, 3, 5, 10, -1, 1000])
            w = word(rng, lo, hi)
            r = rng.random()
            if r < 0.1:
                pl = w + "en"
            elif r < 0.13:
                w = rng.choice(["index", "matrix", "vertex"])
                pl = ""
            else:
                pl = ""
            cases.append([q, w, pl])
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
