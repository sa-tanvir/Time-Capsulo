"""Seeded workload generator for basic_json::erase (range overload). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <kind> TAB <json text> TAB <ops>   (kind = range).
ops is a comma separated list of erase calls applied one after the other to the same value.
Iterator tokens: B = begin(), E = end(), X = begin() of a different value, integer i = i-th element
(array: position at the time of the call; object: i-th member of the original object in ascending key order).
S: hand-written primitives / null / foreign-iterator / empty-range edge cases plus small arrays and objects;
M/L: arrays and objects with 2*10^3 / 3*10^4 members and many erase calls at random positions.
"""
import json, random, sys
from pathlib import Path

KIND = "range"


def elem(rng):
    t = rng.randrange(5)
    if t == 0: return rng.randrange(-100000, 100000)
    if t == 1: return "s" + str(rng.randrange(1000000))
    if t == 2: return [rng.randrange(10) for _ in range(rng.randrange(0, 4))]
    if t == 3: return {"k": rng.randrange(100), "v": "x" * rng.randrange(0, 5)}
    return None if rng.random() < 0.5 else bool(rng.randrange(2))


def make_array(rng, n):
    return [elem(rng) for _ in range(n)]


def make_object(rng, n):
    keys = ["key%07d" % rng.randrange(10 ** 7) for _ in range(n * 2)]
    keys = list(dict.fromkeys(keys))[:n]
    return {k: elem(rng) for k in keys}


def dump(v):
    return json.dumps(v, separators=(",", ":"))


def array_ops(rng, n, count):
    ops, cur = [], n
    for _ in range(count):
        if KIND == "pos":
            if cur < 1: break
            i = rng.choice([0, cur - 1, rng.randrange(cur), rng.randrange(cur)])
            ops.append(str(i)); cur -= 1
        else:
            if cur < 0: break
            i = rng.randrange(cur + 1)
            j = min(cur, i + rng.choice([0, 1, 2, 3, 5, 8]))
            ops.append("%d:%d" % (i, j)); cur -= j - i
    return ops


def object_ops(rng, n, count):
    if KIND == "pos":
        idx = rng.sample(range(n), min(count, n))
        return [str(i) for i in idx]
    cuts = sorted(rng.sample(range(n + 1), min(2 * count, n + 1)))
    pairs = [(cuts[k], cuts[k + 1]) for k in range(0, len(cuts) - 1, 2)]
    rng.shuffle(pairs)
    return ["%d:%d" % p for p in pairs]


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for size in "SML":
        rng = random.Random(20191111 + "SML".index(size))
        lines = []
        if size == "S":
            if KIND == "pos":
                prim = [("5", "B"), ("-7", "B"), ("true", "B"), ("1.5", "B"), ('"abc"', "B"), ('""', "B"), ("null", "B"), ("5", "E"), ('"s"', "E"), ("5", "X"),
                        ("null", "X"), ("[1,2]", "X"), ("[]", "X"), ("null", "E"), ("false", "E"), ("7", "B,B"), ("7", "E,B")]
                arr = [("[1,2,3]", "0"), ("[1,2,3]", "2"), ("[1,2,3]", "1,0"), ("[1,2,3]", "2,1,0"), ("[1]", "0"), ('["a","b"]', "X"), ("[1,2,3]", "0,X,0"),
                       ("[[1],[2,3]]", "1,0")]
                obj = [('{"a":1,"b":2,"c":3}', "0"), ('{"a":1,"b":2,"c":3}', "2"), ('{"a":1,"b":2,"c":3}', "1,2,0"), ('{"x":null}', "0"), ('{"a":1}', "X"),
                       ('{"a":{"b":1},"c":[1,2]}', "0,1")]
            else:
                prim = [("5", "B:E"), ("-7", "B:E"), ("true", "B:E"), ("1.5", "B:E"), ('"abc"', "B:E"), ('""', "B:E"), ("null", "B:E"), ("null", "B:B"), ("5", "B:B"), ("5", "E:E"),
                        ("5", "E:B"), ("5", "X:X"), ("5", "B:X"), ("5", "X:E"), ("null", "X:X"), ("[1,2]", "B:X"), ("false", "B:E,B:E")]
                arr = [("[1,2,3]", "0:3"), ("[1,2,3]", "1:1"), ("[1,2,3]", "0:1"), ("[1,2,3]", "1:3"), ("[1,2,3]", "0:0"), ("[1,2,3]", "3:3"), ("[1,2,3,4,5]", "1:2,0:1,1:2"),
                       ("[]", "0:0"), ("[1,2,3]", "B:E"), ("[1,2,3]", "E:E"), ("[1,2,3]", "X:X"), ("[1,2,3]", "0:X"), ("[[1],[2,3],4]", "1:3")]
                obj = [('{"a":1,"b":2,"c":3}', "0:3"), ('{"a":1,"b":2,"c":3}', "1:2"), ('{"a":1,"b":2,"c":3}', "0:0"), ('{"a":1,"b":2,"c":3}', "3:3"), ('{"a":1,"b":2,"c":3}', "0:1,1:3"),
                       ('{}', "0:0"), ('{"a":1}', "X:X"), ('{"a":1,"b":2}', "B:E"), ('{"a":{"b":1},"c":[1,2],"d":"e"}', "1:2")]
            for t, o in prim + arr + obj:
                lines.append("\t".join(["1", KIND, t, o]))
            for _ in range(8):
                n = rng.randrange(3, 12)
                lines.append("\t".join(["1", KIND, dump(make_array(rng, n)), ",".join(array_ops(rng, n, rng.randrange(1, n)))]))
                n = rng.randrange(3, 12)
                lines.append("\t".join(["1", KIND, dump(make_object(rng, n)), ",".join(object_ops(rng, n, rng.randrange(1, 4)))]))
        else:
            n, count, reps = {"M": (2000, 800, 5), "L": (30000, 8000, 1)}[size]
            for kind_of in ("arr", "obj", "arr"):
                if kind_of == "arr":
                    a = make_array(rng, n); ops = array_ops(rng, n, count)
                else:
                    a = make_object(rng, n); ops = object_ops(rng, len(a), count)
                lines.append("\t".join([str(reps), KIND, dump(a), ",".join(ops)]))
        (out / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")


main()
