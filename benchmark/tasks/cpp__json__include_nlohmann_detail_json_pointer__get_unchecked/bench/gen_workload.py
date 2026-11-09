"""Seeded workload generator for json_pointer::get_unchecked. Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <document json> TAB <pointer> TAB <pointer> ...
The pointers are applied one after the other to the same document (missing members/elements are created on the way).
S: hand-written edge cases (null documents, "-", leading zeros, non-numeric array tokens, primitives in the way, escapes) plus small random cases;
M/L: documents that start as null or as a small object and thousands/ten-thousands of pointers that follow a per-case schema
(object levels with keys from a small vocabulary, array levels with small indices or "-").
"""
import random, sys
from pathlib import Path

VOCAB = ["a", "b", "c", "name", "id", "list", "x", "y", "a/b", "m~n", "", "k1", "k2", "k3"]


def esc(t):
    return t.replace("~", "~0").replace("/", "~1")


def pointer(rng, schema, maxw):
    depth = rng.randrange(1, len(schema) + 1)
    toks = []
    for lvl in range(depth):
        if schema[lvl] == "O":
            toks.append(esc(rng.choice(VOCAB[:4 + 2 * lvl + 2] if lvl < 4 else VOCAB)))
        else:
            toks.append("-" if rng.random() < 0.06 else str(rng.randrange(maxw)))
    return "".join("/" + t for t in toks)


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for size in "SML":
        rng = random.Random(20191111 + "SML".index(size))
        lines = []
        if size == "S":
            iso = [("null", [""]), ("null", ["/a"]), ("null", ["/0"]), ("null", ["/-"]), ("null", ["/a/b/c"]), ("null", ["/0/1/2"]), ("null", ["/"]),
                   ("null", ["/00"]), ("null", ["/-/x"]), ("null", ["/a", "/a/b", "/c/0/d"]),
                   ('{"a":1}', ["/a/b"]), ('{"a":1}', ["/a"]), ('{"a":1}', ["/b"]), ('{"a":{"b":[1,2]}}', ["/a/b/1", "/a/b/-", "/a/b/4"]),
                   ("[1,2]", ["/01"]), ("[1,2]", ["/x"]), ("[1,2]", ["/1x"]), ("[1,2]", ["/-"]), ("[1,2]", ["/5"]), ("[1,2]", ["/0", "/1", "/2"]),
                   ("[1,2]", ["/0/a"]), ('[{"a":1}]', ["/0/a", "/0/b/c"]),
                   ('{"":{"":1}}', ["//"]), ('{"a/b":{"~":2}}', ["/a~1b/~0", "/a~1b/~1"]), ('"str"', ["/0"]), ("true", ["/a"]), ("1.5", ["/0"]), ("-3", ["/x/y"]),
                   ("[]", ["/-/-"]), ("{}", ["/0"]), ('{"a":[1,2,{"b":null}]}', ["/a/2/b/c/0", "/a/-/x"]), ("[null,null]", ["/1/x", "/0/0"]), ("[[1],[2,3]]", ["/1/1", "/1/2", "/0/0/0"]),
                   ("{}", [""]), ('{"a":1}', ["/a/0"])]
            for doc, ps in iso:
                lines.append("\t".join(["1", doc] + ps))
            for _ in range(10):
                schema = "".join(rng.choice("OA") for _ in range(rng.randrange(1, 5)))
                lines.append("\t".join(["1", "null"] + [pointer(rng, schema, 5) for _ in range(rng.randrange(1, 8))]))
        else:
            ncase, nptr, reps = {"M": (6, 3000, 5), "L": (4, 100000, 1)}[size]
            for c in range(ncase):
                schema = "".join(rng.choice("OOA") for _ in range(rng.randrange(3, 7)))
                maxw = rng.choice([4, 12, 40])
                doc = rng.choice(["null", "{}", '{"a":{"b":[1,2,3]},"list":[]}'])
                lines.append("\t".join([str(reps), doc] + [pointer(rng, schema, maxw) for _ in range(nptr)]))
        (out / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")


main()
