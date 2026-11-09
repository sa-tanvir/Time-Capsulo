"""Seeded workload generator for gjson splitPossiblePipe. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (number of random cases, min components, max components)
SIZES = {"S": (500, 1, 4), "M": (200, 25, 40), "L": (60, 250, 400)}
NAMES = ["info", "friends", "first", "last", "name", "a", "b", "c", "age", "extra", "0", "1", "12",
         "fav*", "n?me", "x\\.y", "p\\|q", "@reverse", "@ugly", "@pretty", "k\\\\"]
EDGE = ["hello", "hello.world", "hello|world", "hello\\|world", "hello.#",
        'hello.#[a|1="asdf\\"|1324"]#\\|that', 'hello.#[a|1="asdf\\"|1324"]#|that.more|yikes',
        "a.#[]#\\|b", "a.#|b", "a.#.b|c", "a.#\\|b", "#(a|b)|c", "{a,b}|c", '{"a":b}|c', "{|", "|", "a|",
        ".|x", "a.|b", "a.#(b|c", "a.#[x]|y", 'a.#(b=="x|y")|z', "a.#(b(c)|d)|e", "a.#[b(c|d]|e",
        "{a|b", "{[a]}|x", "{x.#(a|b)}|c", "a.#(b=\"q\\\"|\")#|c", "a|b|c", "", "x.#", "x.#(", "a\\"]
OPS = ["=", "==", "!=", "<", "<=", ">", ">=", "%", "!%"]


def strlit(rng):
    s = "".join(rng.choice("ab|.#()[]{} \\\"") if rng.random() < 0.2 else rng.choice("xyzXYZ019") for _ in range(rng.randint(0, 8)))
    return json.dumps(s)


def query(rng, depth=0):
    o, c = rng.choice(["()", "[]"])
    inner = rng.choice(NAMES[:10])
    if depth < 2 and rng.random() < 0.2:
        inner += "." + query(rng, depth + 1)
    if rng.random() < 0.8:
        inner += rng.choice(OPS) + (strlit(rng) if rng.random() < 0.6 else str(rng.randint(-50, 50)))
    return "#" + o + inner + c + ("#" if rng.random() < 0.5 else "")


def component(rng):
    r = rng.random()
    if r < 0.2:
        return query(rng)
    if r < 0.27:
        return "#"
    return rng.choice(NAMES)


def path(rng, lo, hi):
    n = rng.randint(lo, hi)
    parts = [component(rng) for _ in range(n)]
    out = parts[0]
    for p in parts[1:]:
        out += ("|" if rng.random() < 0.5 / n else ".") + p
    r = rng.random()
    if r < 0.4:
        out += "|" + rng.choice(NAMES)                       # pipe at the very end
    elif r < 0.5:
        out = "{" + ",".join(rng.choice(['"k":', "n:", ""]) + p for p in parts[: max(1, n // 4)]) + "}" + (
            "|" + rng.choice(NAMES) if rng.random() < 0.7 else "")
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20191118 + i)
        cases = list(EDGE) if size == "S" else []
        cases += [path(rng, lo, hi) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
