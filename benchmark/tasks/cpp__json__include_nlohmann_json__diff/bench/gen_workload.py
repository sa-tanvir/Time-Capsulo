"""Seeded workload generator for basic_json::diff. Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <source json> TAB <target json> [TAB <path prefix>]   (compact JSON, no tabs/newlines).
S: hand-written edge cases plus small random pairs; M/L: random documents (about 10^3 / 10^4-10^5 nodes) and
mutated copies of them (changed scalars, changed types, removed/added keys, shortened/extended arrays).
"""
import json, random, sys
from pathlib import Path

KEYS = ["a", "b", "c", "id", "name", "x", "y", "a/b", "~t", "m~n", "", " ", "0", "1", "k/", "/", "~", "~1", "~0"]


def scalar(rng):
    t = rng.randrange(6)
    if t == 0: return None
    if t == 1: return rng.random() < 0.5
    if t == 2: return rng.randrange(-1000, 1000)
    if t == 3: return rng.randrange(0, 20) / 2 + 0.5
    if t == 4: return "".join(rng.choice("abcxyz/~ ") for _ in range(rng.randrange(0, 6)))
    return rng.randrange(0, 10)


def gen(rng, depth, budget):
    """Random value with at most about `budget` nodes."""
    if depth == 0 or budget <= 1 or rng.random() < 0.15:
        return scalar(rng)
    n = rng.randrange(2, 8)
    share = max(1, budget // n)
    if rng.random() < 0.5:
        return [gen(rng, depth - 1, share) for _ in range(n)]
    d = {}
    for _ in range(n):
        d[rng.choice(KEYS) + str(rng.randrange(0, 4)) if rng.random() < 0.5 else rng.choice(KEYS)] = gen(rng, depth - 1, share)
    return d


def mutate(rng, v, p):
    if isinstance(v, list):
        out = [mutate(rng, x, p) for x in v]
        r = rng.random()
        if r < p and out: out = out[:rng.randrange(0, len(out))]
        elif r < 2 * p: out += [scalar(rng) for _ in range(rng.randrange(1, 4))]
        return out
    if isinstance(v, dict):
        out = {k: mutate(rng, x, p) for k, x in v.items()}
        for k in list(out):
            if rng.random() < p: del out[k]
        if rng.random() < p:
            out[rng.choice(KEYS) + "n"] = scalar(rng)
        return out
    if rng.random() < p: return scalar(rng)
    if rng.random() < p / 3: return [scalar(rng)]
    return v


def dump(v):
    return json.dumps(v, separators=(",", ":"))


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for size in "SML":
        rng = random.Random(20191111 + "SML".index(size))
        lines = []
        if size == "S":
            edge = [("1", "1", ""), ("1", "2", ""), ("1", '"a"', '"b"'), ("[]", "[]", ""), ("{}", "{}", ""), ("null", "false", ""),
                    ("[1,2,3]", "[1,2,3]", ""), ("[1,2,3]", "[1,5,3]", ""), ("[1,2,3,4,5]", "[1]", ""), ("[1]", "[1,2,3]", ""),
                    ("[1,2,3,4]", "[9,2]", ""), ('{"a":1}', '{"a":2}', ""), ('{"a":1}', '{"b":1}', ""), ('{"a/b":1,"~":2}', '{"a/b":3,"m~n":4}', ""),
                    ('{"a":[1,{"b":2}]}', '{"a":[1,{"b":3},4]}', ""), ('[[1,2],[3]]', '[[1],[3,4]]', "/root"), ('{"":1}', '{"":[1]}', ""),
                    ('[1,2]', '{"a":1}', "/p/q"), ('{"a":{"b":{"c":1}}}', '{"a":{"b":{}}}', "/x"), ("[1,2,3,4,5,6]", "[1,2,3]", "/arr"),
                    ('[{"a":1},{"b":2}]', '[{"a":1}]', ""), ("1.5", "1.5", "/z"), ('"x"', "null", "/s")]
            for a, b, p in edge:
                lines.append("\t".join(["1", a, b, p]))
            for _ in range(20):
                a = gen(rng, 3, 20)
                lines.append("\t".join(["1", dump(a), dump(mutate(rng, a, 0.25)), rng.choice(["", "", "/base", "/a~1b"])]))
        else:
            ncase, budget, depth, reps = {"M": (12, 600, 7, 6), "L": (8, 30000, 9, 1)}[size]
            for _ in range(ncase):
                a = gen(rng, depth, budget)
                if not isinstance(a, (list, dict)) or len(dump(a)) < 40:
                    a = [gen(rng, depth, budget) for _ in range(4)]
                b = mutate(rng, a, rng.choice([0.02, 0.1, 0.3]))
                lines.append("\t".join([str(reps), dump(a), dump(b), ""]))
        (out / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")


main()
