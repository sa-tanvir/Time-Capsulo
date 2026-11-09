"""Seeded workload generator for gjson tostr. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (number of random cases, min content chars, max content chars)
SIZES = {"S": (500, 0, 40), "M": (200, 300, 600), "L": (60, 3000, 6000)}
CH = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.,:[]{}"
SPECIAL = ['"', '\\', '\n', '\r', '\t', '\b', '\f', '/', 'é', '中', '\U0001F600', '❤']
TAILS = ['', ',', ']', '}', ',"next":[1,2]}', ' , "z":0}', ':', '\n}']
EDGE = ['"hello"', '"hello",1', '"a\\"b",', '"a\\"b"', '"abc', '"ab\\ncd', '""', '"",', '"\\\\"x',
        '"\\u00e9t\\u00e9"}', '"a\tb\\n"', '"a\tb"x', '"\\ud83d\\ude00"]', '"\\ud83d"]', '"x\\\\\\"y"z',
        '"\\/\\b\\f\\r\\t"', '"bad\\q"x', '"\\u12"', '"\\', '"\\"', '"q\\\\"', '"中文",']


def content(rng, lo, hi):
    n = rng.randint(lo, hi)
    p = rng.choice([0.0, 0.02, 0.1])  # some strings need no escaping at all
    return "".join(rng.choice(SPECIAL) if rng.random() < p else rng.choice(CH) for _ in range(n))


def case(rng, lo, hi):
    lit = json.dumps(content(rng, lo, hi), ensure_ascii=rng.random() < 0.5)
    r = rng.random()
    if r < 0.05:
        return lit[:-1]          # unterminated
    if r < 0.15:
        return lit               # closing quote is the last character
    return lit + rng.choice(TAILS)


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20191118 + i)
        cases = list(EDGE) if size == "S" else []
        cases += [case(rng, lo, hi) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
