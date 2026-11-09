"""Seeded workload generator for lodash truncate. Usage: python3 gen_workload.py <out_dir>

Each case: {"seed": int, "n": words, "uni": 0|1, "len": length option or null, "om": omission or null
            ("$null"/"$undef" for explicit null/undefined), "sep": null | {"s": str} | {"re": [src, flags]}}
The driver builds the input text deterministically from `seed`: `n` words from a fixed vocabulary
joined by spaces/commas; with uni=1 some words are astral emoji / combining-mark words.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20190710
SIZES = {"S": (300, 30), "M": (300, 300), "L": (300, 3_000)}
SEPS = [None, None, {"s": " "}, {"s": ","}, {"s": "ho"}, {"s": "zzz"},
        {"re": [",? +", ""]}, {"re": [",? +", "g"]}, {"re": ["\\s", ""]}, {"re": ["[aeiou]{2}", "i"]},
        {"re": ["x$", "m"]}]
OMS = [None, None, "...", " [...]", "", "…", "$null", "$undef", "🚀!"]


def case(rng, max_words):
    n = rng.randint(max_words // 2, max_words)
    approx = n * 6
    r = rng.random()
    if r < 0.1:
        ln = None
    elif r < 0.15:
        ln = rng.choice([0, -2, 1, 2, 3, 4])
    elif r < 0.2:
        ln = approx * 3  # longer than the text: unchanged
    else:
        ln = rng.randint(approx // 4, approx)
    return {"seed": rng.randint(0, 2**31 - 1), "n": n, "uni": int(rng.random() < 0.35),
            "len": ln, "om": rng.choice(OMS), "sep": rng.choice(SEPS)}


FIXED_EXTRA = [  # (driver-recognised literal cases)
    {"lit": "hi-diddly-ho there, neighborino", "len": l, "om": om, "sep": sep}
    for l, om, sep in [(None, None, None), (31, None, None), (33, None, None), (24, None, None),
                       (None, " [...]", None), (None, "$null", None), (None, "$undef", None), (4, None, None),
                       (24, None, {"s": " "}), (24, None, {"re": [",? +", ""]}), (24, None, {"re": [",? +", "g"]}),
                       (0, None, None), (-2, None, None)]
] + [{"lit": "A 🍂, 👨‍❤️‍💋‍👨, and 🚀",
      "len": l, "om": None, "sep": sep} for l, sep in [(13, None), (6, None), (4, {"s": "💕"}),
                                                       (4, {"re": ["💕", ""]})]] + [
    {"lit": "💕" * 10, "len": 4, "om": None, "sep": {"s": "💕"}},
    {"lit": "💕" * 10, "len": 4, "om": None, "sep": {"re": ["💕", ""]}},
    {"lit": "", "len": None, "om": None, "sep": None},
]


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (cnt, m)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        cs = (list(FIXED_EXTRA) if size == "S" else []) + [case(rng, m) for _ in range(cnt)]
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cs))
