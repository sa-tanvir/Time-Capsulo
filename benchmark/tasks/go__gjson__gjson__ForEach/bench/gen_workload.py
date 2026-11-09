"""Seeded workload generator for gjson Result.ForEach. Usage: python3 gen_workload.py <out_dir>
Each case is [Type, Raw, Str, Num, stop]: the Result to iterate and the call number at which the
iterator returns false (0 = never)."""
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

# (number of random cases, approx bytes per document, max nesting depth)
SIZES = {"S": (400, 150, 2), "M": (150, 1500, 3), "L": (60, 15000, 4)}
EDGE = [[0, "", "", 0, 0], [3, '"Hello"', "Hello", 0, 0], [3, "", "Hello", 0, 1], [2, "12.5", "", 12.5, 0],
        [4, "true", "", 0, 0], [1, "false", "", 0, 0], [0, "null", "", 0, 0], [5, "*invalid*", "", 0, 0],
        [5, "", "", 0, 0], [5, "   ", "", 0, 0], [5, '{"bad', "", 0, 0], [5, '{"ok":"bad', "", 0, 0],
        [5, "{}", "", 0, 0], [5, "[]", "", 0, 0], [5, " [ ] ", "", 0, 0],
        [5, ' {"name": {"first": "Janet","last": "Prichard"},\n\t"asd\\nf":"\\ud83d\\udd13","age": 47}', "", 0, 0],
        [5, '[1, "a\\"b", {"x":[1]}, true, false, null, -1.5e3, [], {}]', "", 0, 0],
        [5, '[1,2,3,4]', "", 0, 2], [5, '{"a":1,"b":2,"c":3}', "", 0, 1], [5, '{"a":1,"b":2,"c":3}', "", 0, 3],
        [5, '{"a" : [1,{"b":"]"}] , "c\\"d" : "e\\u00e9"}', "", 0, 0], [5, '{"a":1,"a":2}', "", 0, 0],
        [5, '[1e400, -0, 0.5, "x"]', "", 0, 0], [5, '{"k":nul}', "", 0, 0], [5, '["x",', "", 0, 0],
        [5, '\n\t[ "\\u4e2d" ,\n 3 ]', "", 0, 0]]


def case(rng, budget, depth):
    doc = rand_container(rng, depth, budget)
    raw = dump(rng, doc)
    if rng.random() < 0.2:
        raw = rng.choice([" ", "\n", "\t ", "  "]) + raw
    n = len(doc)
    stop = rng.randint(1, max(1, n)) if rng.random() < 0.15 else 0
    return [5, raw, "", 0, stop]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, budget, depth)) in enumerate(SIZES.items()):
        rng = random.Random(20191118 + i)
        cases = list(EDGE) if size == "S" else []
        cases += [case(rng, budget, depth) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
