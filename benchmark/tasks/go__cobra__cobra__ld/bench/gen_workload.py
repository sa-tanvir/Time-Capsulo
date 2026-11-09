"""Seeded workload generator for cobra.ld. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, min len, max len)
SIZES = {"S": (3000, 0, 12), "M": (300, 40, 120), "L": (40, 400, 1200)}
EDGE = [("", "", False), ("", "abc", True), ("abc", "", False), ("time", "times", True),
        ("tiems", "times", True), ("timeS", "times", False), ("timeS", "times", True),
        ("kitten", "sitting", False), ("é", "e", False), ("É", "é", True), ("İx", "ix", True),
        ("counts", "times", True), ("timezone", "times", True), ("ab", "ba", False)]
ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJ-_0123"

def word(rng, n):
    return "".join(rng.choice(ALPHA) for _ in range(n))

def mutate(rng, s, k):
    s = list(s)
    for _ in range(k):
        op = rng.randrange(3)
        p = rng.randrange(len(s) + 1)
        if op == 0 or not s:
            s.insert(p, rng.choice(ALPHA))
        elif op == 1:
            del s[min(p, len(s) - 1)]
        else:
            s[min(p, len(s) - 1)] = rng.choice(ALPHA)
    return "".join(s)

def cases(n, lo, hi, rng, edge):
    out = [list(e) for e in EDGE] if edge else []
    while len(out) < n:
        a = word(rng, rng.randint(lo, hi))
        if rng.random() < 0.6:
            b = mutate(rng, a, rng.randint(0, max(1, len(a) // 4)))
        else:
            b = word(rng, rng.randint(lo, hi))
        out.append([a, b, rng.random() < 0.5])
    return out

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20190607 + i)
        doc = {"cases": cases(n, lo, hi, rng, size == "S")}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(doc))
