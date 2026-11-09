"""Seeded workload generator for binary_writer::write_ubjson. Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <json document, compact> TAB <mode>.   mode = plain | count | type
(plain: use_count=false, use_type=false; count: use_count=true; type: use_count=true and use_type=true).
S: hand-written values for every JSON type and every integer width boundary, empty and nested containers, homogeneous / heterogeneous containers;
M/L: random documents (about 3 * 10^3 / 3 * 10^5 nodes) rich in homogeneous arrays and objects (so that the typed form is used), in all three modes.
"""
import json, random, sys
from pathlib import Path

WORDS = ["alpha", "beta", "gamma", "delta", "id", "name", "value", "k", "x", "y", "z", "list", "data", "eé", "€", "", "a b"]


def scalar(rng):
    t = rng.randrange(9)
    if t == 0: return None
    if t == 1: return rng.random() < 0.5
    if t == 2: return rng.randrange(-130, 130)
    if t == 3: return rng.randrange(130, 70000) * rng.choice([1, -1])
    if t == 4: return rng.choice([rng.randrange(-2 ** 31, 2 ** 31), rng.randrange(-2 ** 62, 2 ** 62), rng.randrange(2 ** 31, 2 ** 63)])
    if t == 5: return rng.randrange(-2000, 2000) / 8.0
    if t == 6: return rng.randrange(-10 ** 7, 10 ** 7) / 1000.0
    return "".join(rng.choice("abcdefghij é€") for _ in range(rng.choice([0, 1, 1, 2, 5, 20])))


def homogeneous(rng, n):
    t = rng.randrange(8)
    if t == 0: return [rng.randrange(-100, 100) for _ in range(n)]
    if t == 1: return [rng.randrange(0, 255) for _ in range(n)]
    if t == 2: return [rng.randrange(-30000, 30000) for _ in range(n)]
    if t == 3: return [rng.randrange(-2 ** 31, 2 ** 31) for _ in range(n)]
    if t == 4: return [rng.choice([True, False])] * n
    if t == 5: return ["w" + str(rng.randrange(1000)) for _ in range(n)]
    if t == 6: return [rng.randrange(-1000, 1000) / 4.0 for _ in range(n)]
    return [None] * n


def gen(rng, depth, budget):
    if depth == 0 or budget <= 1 or rng.random() < 0.3:
        return scalar(rng)
    r = rng.random()
    n = rng.randrange(0, 9)
    share = max(1, budget // max(n, 1))
    if r < 0.3:
        return homogeneous(rng, n)
    if r < 0.4:
        # object whose values are all of one kind
        h = homogeneous(rng, n)
        return {rng.choice(WORDS) + str(i): x for i, x in enumerate(h)}
    if r < 0.55:
        # array of equally shaped arrays / objects
        return [homogeneous(rng, rng.randrange(0, 5)) for _ in range(n)] if rng.random() < 0.5 else [{"a": rng.randrange(100), "b": "x"} for _ in range(n)]
    if r < 0.8:
        return [gen(rng, depth - 1, share) for _ in range(n)]
    return {rng.choice(WORDS) + str(i): gen(rng, depth - 1, share) for i in range(n)}


def dump(v):
    return json.dumps(v, separators=(",", ":"))


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for size in "SML":
        rng = random.Random(20191111 + "SML".index(size))
        lines = []
        if size == "S":
            vals = [None, True, False, 0, 1, 127, 128, 255, 256, 32767, 32768, 65535, 65536, 2147483647, 2147483648, 4294967296, 9223372036854775807,
                    -1, -128, -129, -255, -256, -32768, -32769, -2147483648, -2147483649, -9223372036854775808, 1.5, -0.25, 1e300, "", "a", "hello", "é€",
                    [], {}, [[]], [{}], [None], [1, 2, 3], [1, 200, 3], [-1, -2], [True, True], [True, False], [None, None], ["a", "bc"], [1.5, 2.5], [1, 1.5],
                    [[1, 2], [3]], [[1], [2]], [{"a": 1}, {"b": 2}], [{"a": 1}, [1]], {"a": 1}, {"a": 1, "b": 2}, {"a": 1, "b": 300}, {"a": True, "b": True},
                    {"a": "x", "b": "y"}, {"a": [1], "b": [2]}, {"a": {"c": 1}, "b": {"d": 2}}, {"": 0}, {"k": [1, 2, 3], "j": [True]}, [[1, 2], [3, 4], [5, 6]],
                    [[[]]], [[], []], [{}, {}], {"a": [], "b": []}, {"a": {}}, [1, [2, [3, [4]]]], ["x" * 200], {"k" * 130: 1}, [0] * 130, [255] * 5, [256] * 5]
            for v in vals:
                for mode in ("plain", "count", "type"):
                    lines.append("\t".join(["1", dump(v), mode]))
            for _ in range(30):
                v = gen(rng, 3, 30)
                for mode in ("plain", "count", "type"):
                    lines.append("\t".join(["1", dump(v), mode]))
        else:
            ndoc, budget, depth, reps = {"M": (6, 4000, 6, 4), "L": (6, 300000, 8, 1)}[size]
            for c in range(ndoc):
                v = {"d%d" % i: gen(rng, depth, budget // 8) for i in range(8)}
                v["big"] = homogeneous(rng, budget // 6)
                mode = ("plain", "count", "type")[c % 3]
                lines.append("\t".join([str(reps), dump(v), mode]))
                if c < 3:
                    lines.append("\t".join([str(reps), dump(v), ("count", "type", "plain")[c % 3]]))
        (out / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")


main()
