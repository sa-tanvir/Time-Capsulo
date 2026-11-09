"""Seeded workload generator for gjson unescape. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (number of random cases, min content chars, max content chars)
SIZES = {"S": (500, 0, 40), "M": (200, 300, 600), "L": (60, 3000, 6000)}
CH = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.,:[]{}"
SPECIAL = ['"', '\\', '\n', '\r', '\t', '\b', '\f', '/', '\u00e9', '\u4e2d', '\U0001F600', '\u2764', '\x01']
ODD = ['\\ud83d', '\\ude00', '\\ude00\\ud83d', '\\ud83dx', '\\uD83D\\uDE00', '\\uzzzz', '\\u00E9', '\\/']
STOP = ['\\q', '\x07', '\\u12', '\\']
EDGE = ['', 'plain text', '\\\\\x00', '\\/\\b\\f', '\\"quoted\\"', 'tab\\there', '\\u00e9t\\u00e9',
        '\\ud83d\\ude00', '\\ud83d', '\\ud83dabc', '\\ude00\\ud83d', '\\ud83d\\u0041', '\\uD834\\uDD1E',
        '\\u0000x', '\\uzzzzx', '\\u12', '\\u123', 'ab\\', 'ab\\x', 'a\nb', 'a\x7fb', '\u4e2d\\u4e2d',
        '\\\\\\\\', '\\ud83d\\uzzzz', '\\ud83d\\u12', 'end\\ud83d\\']


def body(rng, lo, hi):
    n = rng.randint(lo, hi)
    p = rng.choice([0.02, 0.1, 0.3])
    s = "".join(rng.choice(SPECIAL) if rng.random() < p else rng.choice(CH) for _ in range(n))
    b = json.dumps(s, ensure_ascii=rng.random() < 0.6)[1:-1]
    # sprinkle surrogate oddities / invalid hex
    if rng.random() < 0.3:
        k = rng.randint(0, len(b))
        while k > 0 and b[k - 1] == "\\":
            k -= 1
        b = b[:k] + rng.choice(ODD) + b[k:]
    if rng.random() < 0.05:  # something that stops the decoding
        k = rng.randint(len(b) // 2, len(b))
        while k > 0 and b[k - 1] == "\\":
            k -= 1
        b = b[:k] + rng.choice(STOP) + b[k:]
    return b


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lo, hi)) in enumerate(SIZES.items()):
        rng = random.Random(20191118 + i)
        cases = list(EDGE) if size == "S" else []
        cases += [body(rng, lo, hi) for _ in range(n)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
