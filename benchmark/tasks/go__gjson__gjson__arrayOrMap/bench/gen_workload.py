"""Seeded workload generator for gjson Result.arrayOrMap. Usage: python3 gen_workload.py <out_dir>
Each case is [Raw, vc, valueize]: arrayOrMap is called on Result{Type: JSON, Raw: Raw} with vc (0, 91 = "[",
123 = "{") and valueize."""
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
A, O = 91, 123
EDGE = []
for raw in ["**invalid**", "{", "[", '"asdf"', "   ", "", '{"asdf":"ghjk"', '{"name": "Alex","name": "Peter"}',
            '{"array": ["PERSON1","PERSON2",0],}', '[1,[2,3],{"a":"b"},true,false,null,"s\\"q"]', "{1:2,true:3}",
            '{"a":1,"b"}', "[x, 1]", '{"a":-}', ' \n [ "\\u00e9", -1.5e3, 1e400 ] ', '{"a":{"b":[1,2]},"c":"]"}',
            "[]", "{}", '["a\\u0000b", "\\ud83d\\ude00"]', "[1 2 3]", '{"a" "b" "c" "d"}', "[nul, tru, fals]",
            '{"k":[1,2,3}', "[-, -1, 0.5e-3, 5E+2]", '{"":1,"":2}']:
    for vc in (0, A, O):
        for val in (False, True):
            EDGE.append([raw, vc, val])


def case(rng, budget, depth):
    kind = rng.choice("[{")
    raw = dump(rng, rand_container(rng, depth, budget, kind))
    if rng.random() < 0.2:
        raw = rng.choice([" ", "\n", "\t "]) + raw
    r = rng.random()
    if r < 0.4:
        vc = 0
    elif r < 0.95:
        vc = ord(kind)
    else:
        vc = A if kind == "{" else O   # kind mismatch
    return [raw, vc, rng.random() < 0.5]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, budget, depth)) in enumerate(SIZES.items()):
        rng = random.Random(20191118 + i)
        cases = list(EDGE) if size == "S" else []
        cases += [case(rng, budget, depth) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
