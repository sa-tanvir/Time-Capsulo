"""Seeded workload generator for utils.encode. Usage: python3 gen_workload.py <out_dir>

Each case is {"v": value, "rep": k, "charset": c}. If v is a string the driver passes v repeated k times;
{"$buf": text} becomes a Buffer and {"$sym": desc} a Symbol; numbers/booleans are passed as is.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20191108
# (number of random cases, max base length, max repetition): mean string length ~90 / ~900 / ~10000
SIZES = {"S": (300, 40, 8), "M": (300, 60, 60), "L": (300, 80, 500)}

ALPHABETS = [
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~",
    " !\"#$%&'()*+,/:;<=>?@[\\]^`{|}\t\n",
    "äöüßæéñçøåÀÿ \u0080",
    "€✓☺אбвгд日本語漢字￿ࠀ",
    "𐐷😀🎉𝄞",
]
CHARSETS = ["utf-8", "utf-8", "iso-8859-1", None]


def rstr(rng, n):
    weights = [rng.random() for _ in ALPHABETS]
    out = []
    for _ in range(rng.randint(1, n)):
        alpha = rng.choices(ALPHABETS, weights)[0]
        out.append(rng.choice(alpha))
    return "".join(out)


FIXED = ["", "b", "A_Z", "€", "", "א", "𐐷", "b c", "a[b]", "~q1!2\"'w$5&7/z8)?", "@*_+-./~ !",
         "æ", "✓", "☺", "\ud800", "\udc00a", "x\ud83d", 12.5, -7, 0, True, False,
         {"$buf": "a b"}, {"$buf": ""}, {"$buf": "€x"}, {"$sym": "Symbol.iterator"}, {"$sym": ""}]


def cases(n, max_len, max_rep, rng, with_fixed):
    out = []
    if with_fixed:
        for v in FIXED:
            for cs in ["utf-8", "iso-8859-1", None]:
                out.append({"v": v, "rep": 1, "charset": cs})
    for _ in range(n):
        out.append({"v": rstr(rng, max_len), "rep": rng.randint(1, max_rep), "charset": rng.choice(CHARSETS)})
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m, r)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, m, r, rng, size == "S")))
