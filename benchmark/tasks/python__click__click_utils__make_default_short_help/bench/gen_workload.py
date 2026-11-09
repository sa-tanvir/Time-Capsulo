"""Seeded workload generator for make_default_short_help. Usage: python3 gen_workload.py <out_dir>

Each case is (help_text, max_length). Per-case scale grows ~10x per size: help texts of ~K words and
max_length up to ~6*K characters, K = 10 (S), 100 (M), 1000 (L)."""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (10, 3000), "M": (100, 1000), "L": (1000, 200)}   # (K words, cases)
EDGE = [["", 45], ["   \n ", 45], ["This is a short text.", 45], ["Login and store the token in ~/.netrc.", 45],
        ["This is a long text that is too long to show as short help\n    and will be truncated instead.", 45],
        ["This is a long text that is too long to show as short help\n    and will be truncated instead.", 61],
        ["First sentence. Second sentence.", 45], ["Supercalifragilistic word", 10], ["one two three", 7],
        ["one two three", 13], ["one two three", 0], ["Use e.g. this", 45], ["v1.2 is out", 45], ["a.", 1], ["a.", 2]]
SEPS = [" "] * 12 + ["  ", "\n", "\n    ", "\t", " \n\n  "]


def word(rng):
    w = "".join(rng.choice(string.ascii_letters + "~/-_.,:") for _ in range(rng.randint(1, 12)))
    if w.endswith(".") and rng.random() < 0.9:
        w = w[:-1] + "x"
    return w


def case(rng, K):
    n = rng.randint(0, 2 * K)
    words = [word(rng) for _ in range(n)]
    if words and rng.random() < 0.3:
        words[rng.randrange(len(words))] += "."
    text = rng.choice(["", " ", "\n    "]) + "".join(w + rng.choice(SEPS) for w in words)
    max_length = rng.randint(0, 7 * K)
    return [text, max_length]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (K, n)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        cases = [case(rng, K) for _ in range(n)]
        if size == "S":
            cases = EDGE + cases
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
