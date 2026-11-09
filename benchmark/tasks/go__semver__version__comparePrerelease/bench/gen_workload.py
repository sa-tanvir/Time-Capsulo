"""Seeded workload generator for semver comparePrerelease. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# size: (pairs, max identifiers per pre-release, inner repetitions per pass)
SIZES = {"S": (20_000, 3, 2), "M": (20_000, 12, 1), "L": (4_000, 80, 1)}
WORDS = ["alpha", "beta", "rc", "pre", "dev", "SNAPSHOT", "FOO", "BAR", "x", "Y", "a", "b", "-1", "-2", "-3"]
EDGE = [
    ("beta", "beta"), ("alpha", "beta"), ("beta.2", "beta.1"), ("beta2", "beta1"), ("beta", "beta.2"),
    ("beta", "beta.foo"), ("beta.2", "beta"), ("beta.foo", "beta"), ("beta.4", "beta.-2"),
    ("beta.-2", "beta.-3"), ("beta.-3", "beta.5"), ("SNAPSHOT.99", "SNAPSHOT.103"),
    ("SNAPSHOT.FOO", "SNAPSHOT.103"), ("SNAPSHOT.99", "SNAPSHOT.BAR"), ("alpha.1", "alpha.beta"),
    ("1", "2"), ("10", "9"), ("rc.1", "rc.1"), ("0", "a"), ("Z", "a"), ("a-b", "a"),
    ("18446744073709551615", "1"), ("18446744073709551616", "1"), ("99999999999999999999", "a"),
    ("", "alpha"), ("alpha", ""), ("", ""),
]

def ident(rng):
    r = rng.random()
    if r < 0.45:
        return str(rng.choice([0, rng.randint(1, 9), rng.randint(10, 999), rng.randint(1000, 10**15)]))
    if r < 0.8:
        return rng.choice(WORDS)
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
    return rng.choice("abcdefghijklmnopqrstuvwxyzA-") + "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 8)))

def pre(rng, kmax):
    return [ident(rng) for _ in range(rng.randint(max(1, kmax // 3), kmax))]

def pair(rng, kmax):
    a = pre(rng, kmax)
    b = list(a)
    r = rng.random()
    if r < 0.15:
        pass                                     # identical
    elif r < 0.6:
        b[rng.randrange(len(b))] = ident(rng)    # one identifier differs (often late)
    elif r < 0.75:
        b = b[:rng.randrange(len(b))] if len(b) > 1 else b + [ident(rng)]   # prefix
    elif r < 0.9:
        b = b + [ident(rng) for _ in range(rng.randint(1, 3))]              # extension
    else:
        b = pre(rng, kmax)                       # unrelated
    if rng.random() < 0.5:
        a, b = b, a
    return [".".join(a), ".".join(b)]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, kmax, inner)) in enumerate(SIZES.items()):
        rng = random.Random(20191213 + i)
        cases = [list(e) for e in EDGE] if size == "S" else []
        while len(cases) < n:
            cases.append(pair(rng, kmax))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"inner": inner, "cases": cases}))
