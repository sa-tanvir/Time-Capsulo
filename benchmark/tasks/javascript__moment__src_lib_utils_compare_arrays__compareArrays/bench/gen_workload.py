"""Seeded workload generator for compareArrays(array1, array2, dontConvert).
Usage: python3 gen_workload.py <out_dir>

Each case is [array1, array2] or [array1, array2, dontConvert]. Elements are what moment passes in
practice: date-part numbers (as from toArray()), numeric strings, locale-name parts, plus a few
non-numeric / fractional / negative values. S/M/L grow the array length (~10 / ~100 / ~1000).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190121
SIZES = {"S": (600, 12), "M": (500, 120), "L": (400, 1200)}
WORDS = ["en", "gb", "au", "fr", "ca", "zh", "cn", "tw", "x", "pseudo", "sr", "cyrl", "de", "at"]

FIXED = [
    [["en", "au"], ["en", "gb"], True], [["en"], ["en", "gb"], True], [["en", "gb"], ["en"], True],
    [[], [], True], [[], [1, 2, 3]], [[2010, 1, 14, 15, 25, 50, 125], [2010, 1, 14, 15, 25, 50, 125]],
    [[2010, 1, 14], [2010, 1, 15, 0]], [["1", "2"], [1, 2]], [["1", "2"], [1, 2], True], [["1.9", -2.7], [1, -2]],
    [["abc", None], [0, 0]], [[None], [None], True], [["x"], ["y"], False], [[1, 2, 3], [3, 2, 1], 0],
    [["Infinity", float("1e300")], [0, 1]], [["-0", 0], [0, "0"], True], [["", " "], [0, 0]],
]


def elem(rng, kind):
    if kind == 0:
        return rng.randint(-5, 3000)
    if kind == 1:
        return str(rng.randint(0, 3000))
    if kind == 2:
        return rng.choice(WORDS)
    return rng.choice([rng.randint(0, 60), round(rng.uniform(-50, 50), 2), str(round(rng.uniform(-9, 9), 1)), "n/a", None])


def case(rng, n):
    kind = rng.randint(0, 3)
    a = [elem(rng, kind) for _ in range(n)]
    b = list(a)
    for _ in range(rng.randint(0, max(1, n // 3))):
        if b:
            b[rng.randrange(len(b))] = elem(rng, rng.choice([kind, kind, rng.randint(0, 3)]))
    r = rng.random()
    if r < 0.2:
        b = b[:rng.randint(0, len(b))]
    elif r < 0.4:
        b = b + [elem(rng, kind) for _ in range(rng.randint(1, max(1, n // 4)))]
    if rng.random() < 0.5:
        a, b = b, a
    dc = rng.choice([None, True, False])
    return [a, b] if dc is None else [a, b, dc]


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for i, (size, (count, n)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cases = (list(FIXED) if size == "S" else []) + [case(rng, rng.randint(n // 2, n * 3 // 2)) for _ in range(count)]
        (out / f"workload_{size}.json").write_text(json.dumps(cases, separators=(",", ":")))
