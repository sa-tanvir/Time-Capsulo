"""Seeded workload generator for gjson parseQuery. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (number of random cases, min chars, max chars of the left path / right value)
SIZES = {"S": (500, 1, 12), "M": (200, 100, 250), "L": (60, 1000, 2500)}
NAMES = ["first_name", "age", "a", "b", "service_roles", "details.city", "x\\(y", "q\\=r", "n?me", "0"]
OPS = ["=", "==", "!=", "<", "<=", ">", ">=", "%", "!%"]
REST = ["", ".last", "|#", ".0.name", "#", "#.x", "#|@reverse", ")", " tail"]
EDGE = ['#(service_roles.#(=="one").()==asdf).cap', '#(first_name%"Murphy").last',
        '#( first_name !% "Murphy" ).last', '#(service_roles.#(=="one"))',
        '#(a\\("\\"(".#(=="o\\"(ne")%"ab\\")").remain', '#[age=101].x', '#(a!b)', '#(a=)', '#(a==)', '#(=)',
        '#()', '#[]#|#', '#(a>=1)#', '#(a<"x")', '#(a', '#', '(', 'x(a=1)', '#(a="b)', '#(a\\)', '#(a]',
        '#(a=1)]', '#(a!=)', '#(a<)', '#(  a  ==  "b"  )rest', '#[a%"x*"]#.b', '#(a!%"*")', '#(a>"(")x',
        '#(a\t=\ttrue\n)', '#(a=[1,2])', '#(a.#(b=1)=2)', '#(%"j*")', '#(!=1)', '#(a=!=b)', '##(a)', '']


def pick_len(rng, lo, hi):
    return rng.randint(lo, hi)


def rand_name(rng, n):
    out = rng.choice(NAMES)
    while len(out) < n:
        out += "." + rng.choice(NAMES)
    return out


def rand_value(rng, n):
    r = rng.random()
    if r < 0.6:
        s = "".join(rng.choice("()[]\"\\*?,.| ") if rng.random() < 0.15 else rng.choice("abcXYZ019")
                    for _ in range(n))
        return json.dumps(s)
    if r < 0.8:
        return str(rng.randint(-10 ** min(n, 15), 10 ** min(n, 15)))
    return rng.choice(["true", "false", "null"])


def ws(rng):
    return rng.choice(["", "", "", " ", "  ", "\t"])


def query(rng, lo, hi, depth=0):
    o, c = rng.choice(["()", "[]"])
    left = rand_name(rng, pick_len(rng, lo, hi))
    if depth < 3 and rng.random() < 0.3:
        left += "." + query(rng, max(1, lo // 3), max(2, hi // 3), depth + 1)
    if rng.random() < 0.15:
        return "#" + o + ws(rng) + left + ws(rng) + c
    return "#" + o + ws(rng) + left + ws(rng) + rng.choice(OPS) + ws(rng) + rand_value(rng, pick_len(rng, lo, hi)) + ws(rng) + c


def case(rng, lo, hi):
    q = query(rng, lo, hi) + rng.choice(REST)
    r = rng.random()
    if r < 0.04:
        return q[: rng.randint(2, len(q) - 1)]   # possibly unbalanced
    if r < 0.06:
        return rng.choice(["", "x", "#a", "(#"]) + q  # does not start with #( or #[
    return q


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20191118 + i)
        cases = list(EDGE) if size == "S" else []
        cases += [case(rng, lo, hi) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
