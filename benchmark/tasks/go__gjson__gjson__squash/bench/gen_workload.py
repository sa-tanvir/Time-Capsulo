"""Seeded workload generator for gjson squash. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# ---- shared seeded JSON document generator (stdlib only) ----
import json as _json

_CH = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.,:"
_SPECIAL = ['"', '\\', '\n', '\t', '/', '[', ']', '{', '}', '(', ')', 'é', '中', '\U0001F600', '|', '#']


def rand_str(rng, n):
    out = []
    for _ in range(n):
        out.append(rng.choice(_SPECIAL) if rng.random() < 0.08 else rng.choice(_CH))
    return "".join(out)


def rand_scalar(rng):
    r = rng.random()
    if r < 0.45:
        return rand_str(rng, rng.randint(0, 16))
    if r < 0.6:
        return rng.randint(-10**6, 10**6)
    if r < 0.75:
        return round(rng.uniform(-1e4, 1e4), rng.randint(0, 6))
    if r < 0.8:
        return rng.choice([1.5e-7, -2.25e21, 6.02e23, 0, -0.5])
    return rng.choice([True, False, None])


def rand_value(rng, depth, budget):
    """A random JSON value of roughly `budget` serialized bytes and nesting <= depth."""
    if depth == 0 or budget < 24:
        return rand_scalar(rng)
    if rng.random() < 0.5:
        obj, used = {}, 2
        while used < budget:
            k = rand_str(rng, rng.randint(1, 10))
            v = rand_value(rng, depth - 1, budget // rng.randint(3, 8)) if rng.random() < 0.35 else rand_scalar(rng)
            obj[k] = v
            used += len(_json.dumps({k: v}))
        return obj
    arr, used = [], 2
    while used < budget:
        v = rand_value(rng, depth - 1, budget // rng.randint(3, 8)) if rng.random() < 0.35 else rand_scalar(rng)
        arr.append(v)
        used += len(_json.dumps(v)) + 1
    return arr


def dump(rng, v):
    """Serialize with a random style: compact / spaced / indented, ASCII-escaped or raw UTF-8."""
    style = rng.randint(0, 2)
    kw = {"ensure_ascii": rng.random() < 0.5}
    if style == 0:
        kw["separators"] = (",", ":")
    elif style == 2:
        kw["indent"] = rng.choice([1, 2, "\t"])
    return _json.dumps(v, **kw)


def rand_container(rng, depth, budget, kind=None):
    kind = kind or rng.choice("[{")
    while True:
        v = rand_value(rng, depth, budget)
        if (kind == "{" and isinstance(v, dict)) or (kind == "[" and isinstance(v, list)):
            return v
# ---- end shared generator ----

# (number of random cases, approx bytes of the leading value, max nesting depth)
SIZES = {"S": (400, 120, 2), "M": (150, 1500, 3), "L": (60, 15000, 5)}
EDGE = ['[]', '{}', '()', '""', '"a\\"b"x', '"a\\\\"b', '"\\\\\\""tail', '[}', '[1,2', '{"a":"]"}tail',
        '["\\\\"]x', '[("]")]x', '{"a":[1,{"b":2}]},3', '(a(b)c) d', '[[[]]]]]', '{"a":"\\"}"}rest',
        '"]"', '"" ', '[1]   [2]', '{"k":"v"', '["unterminated', '(x=="y)")#.z']
TAILS = ['', ',', ']', '}', ',"next":[1,2]}', ' , {"z":0}]', '|@reverse', '.rest', ' ']


def case(rng, budget, depth):
    r = rng.random()
    tail = rng.choice(TAILS)
    if r < 0.15:
        return dump(rng, rand_str(rng, max(1, budget // 2))) + tail
    doc = dump(rng, rand_container(rng, depth, budget))
    if r < 0.25:
        doc = "(" + doc[1:-1] + ")"
    elif r < 0.30:
        return doc[: rng.randint(1, len(doc) - 1)]  # unterminated container
    return doc + tail


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, budget, depth)) in enumerate(SIZES.items()):
        rng = random.Random(20191118 + i)
        cases = list(EDGE) if size == "S" else []
        cases += [case(rng, budget, depth) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
