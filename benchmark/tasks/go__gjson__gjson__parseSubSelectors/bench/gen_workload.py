"""Seeded workload generator for gjson parseSubSelectors. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (number of random cases, min selectors, max selectors)
SIZES = {"S": (500, 1, 4), "M": (200, 20, 40), "L": (60, 200, 400)}
NAMES = ["info", "friends", "first", "last", "age", "extra", "0", "1", "a", "b", "fav*", "x\\,y", "p\\:q", "k\\]"]
REST = ["", "|@ugly", ".@pretty", "|0.first", ".abc", "|#", "}", ",x"]
EDGE = ["[]", "{}", "[a]", "{a,b}", "[0.first,1.extra.0]", "[first,extra.0]", "{age,first|@case:upper}|@ugly",
        "{friends.#.{age,first:first|@case:upper}|0.first}",
        '{abc:info.friends.0.first,info.friends.1.last,"a\ra":info.friends.0.kind,"abc":info.friends.1.kind,'
        '{123:info.friends.1.cust2},[info.friends.#[details.city="Phoenix"]#|#]}.@pretty.@ugly',
        "{a.@x,b:c}", "[a:b]", "{a:b:c}", "{a,}", "{,}", "{a", "[a,[b,c]", "{a\\,b,c}", '{"x,y":z}',
        "{a(b,c),d}", "{@x:y,z:w}", "{a|@m:1,b:c}", "{a.#(b==\"x,y\")#,c}", "{\"q\\\"}\":r}rest", "[a]]]",
        "{a:[b,c],d:{e:f}}tail", "[x)", "{:a}", "{a:}"]
OPS = ["=", "==", "!=", "<", ">=", "%"]


def path(rng, depth):
    r = rng.random()
    if depth < 2 and r < 0.12:
        return multipath(rng, depth + 1, 1, 4)
    p = rng.choice(NAMES)
    for _ in range(rng.randint(0, 3)):
        p += "." + rng.choice(NAMES)
    if rng.random() < 0.15:
        p += ".#(" + rng.choice(NAMES[:6]) + rng.choice(OPS) + json.dumps(rng.choice(["x,y", "a:b", "}]", "plain", "q\"r"])) + ")#"
    if rng.random() < 0.1:
        p += rng.choice(["|@reverse", ".@ugly", "|@case:upper", "|#"])
    return p


def selector(rng, depth):
    r = rng.random()
    if r < 0.3:
        return rng.choice(NAMES[:8]) + ":" + path(rng, depth)
    if r < 0.4:
        return json.dumps(rng.choice(["a,b", "x:y", "n}", "plain", "q\"z"])) + ":" + path(rng, depth)
    return path(rng, depth)


def multipath(rng, depth, lo, hi):
    o, c = rng.choice(["[]", "{}"])
    return o + ",".join(selector(rng, depth) for _ in range(rng.randint(lo, hi))) + c


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20191118 + i)
        cases = list(EDGE) if size == "S" else []
        for _ in range(n):
            m = multipath(rng, 0, lo, hi)
            if rng.random() < 0.05:
                m = m[:-1]  # never closed
            cases.append(m + rng.choice(REST))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
