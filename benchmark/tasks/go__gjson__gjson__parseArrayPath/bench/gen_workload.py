"""Seeded workload generator for gjson parseArrayPath. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (number of random cases, min chars, max chars of names / query parts)
SIZES = {"S": (500, 1, 12), "M": (200, 100, 250), "L": (60, 1000, 2500)}
NAMES = ["friends", "age", "a", "b", "0", "12", "first_name", "n?me", "fav*", "x\\.y", "@reverse"]
OPS = ["=", "==", "!=", "<", "<=", ">", ">=", "%", "!%"]
EDGE = ["", "#", "##", "#.", "#.name", "#.name.first", "#|x", "#(a=1)", "#(a=1)#", "#(a=1)#.b", "#(a=1).b",
        "#(a=1)|b", "#(a=1)#|#", "#[first%\"D*\"]#.last", "#(a", "#(a.b", "#(a=\"x.y|z\")#.c", "#x.y", "a#b.c",
        "a.b", "a|b", "a\\.b.c", "abc", "0", "0.1", "#(b(c)=1)rest.x", "#(service_roles.#(==\"one\"))#.v",
        "#( a > 5 )", "#()", "#[]#", "#(a)", "#(a=1)x#.y", "#(a!b)", "##(a=1)", ".a", "|a", "#.#.a", "#.|x",
        "a.#(b=1)", "#(a=1)#x.y"]


def rand_name(rng, n):
    out = rng.choice(NAMES)
    while len(out) < n:
        out += rng.choice(NAMES)
    return out


def rand_value(rng, n):
    r = rng.random()
    if r < 0.6:
        s = "".join(rng.choice("()[]\"\\*?,.| #") if rng.random() < 0.15 else rng.choice("abcXYZ019")
                    for _ in range(n))
        return json.dumps(s)
    if r < 0.8:
        return str(rng.randint(-10 ** min(n, 15), 10 ** min(n, 15)))
    return rng.choice(["true", "false", "null"])


def query(rng, lo, hi, depth=0):
    o, c = rng.choice(["()", "[]"])
    left = rand_name(rng, rng.randint(lo, hi))
    if depth < 2 and rng.random() < 0.3:
        left += ".#" + query(rng, max(1, lo // 3), max(2, hi // 3), depth + 1)[1:]
    if rng.random() < 0.15:
        return "#" + o + left + c
    return "#" + o + left + rng.choice(["", " "]) + rng.choice(OPS) + rng.choice(["", " "]) + rand_value(rng, rng.randint(lo, hi)) + c


def rest(rng, lo, hi):
    if rng.random() < 0.3:
        return ""
    return rng.choice([".", "|"]) + ".".join(rng.choice(NAMES + ["#", "#.x"]) for _ in range(rng.randint(1, 3)))


def case(rng, lo, hi):
    r = rng.random()
    if r < 0.15:
        first = rand_name(rng, rng.randint(lo, hi))
        if rng.random() < 0.3:
            k = rng.randint(0, len(first))
            first = first[:k] + "#" + first[k:]
    elif r < 0.3:
        first = "#." + rand_name(rng, rng.randint(lo, hi))
    elif r < 0.35:
        first = "#"
    else:
        first = query(rng, lo, hi) + ("#" if rng.random() < 0.5 else "")
        if rng.random() < 0.05:
            first = first[: rng.randint(2, len(first) - 1)]  # unbalanced query
    return first + rest(rng, lo, hi)


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20191118 + i)
        cases = list(EDGE) if size == "S" else []
        cases += [case(rng, lo, hi) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
