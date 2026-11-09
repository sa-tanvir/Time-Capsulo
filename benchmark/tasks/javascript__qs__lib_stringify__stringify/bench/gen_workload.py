"""Seeded workload generator for qs.stringify benches. Usage: python3 gen_workload.py <out_dir>

Each case is {"obj": <tagged JSON>, "opts": <tagged JSON or null>}. Non-JSON values are tagged as
single-key objects and rebuilt by the driver: {"$date": ms}, {"$buf": text}, {"$undef": 1},
{"$sym": description}, {"$fn": name} (named sort/filter/encoder/serializeDate functions).
"""
import json, random, sys
from pathlib import Path

RELEASE = 20191108
# (number of random cases, mean leaf values per case): per-case input grows ~10x per size step
SIZES = {"S": (80, 8), "M": (80, 100), "L": (80, 1200)}

KEY_PARTS = ["a", "b", "id", "name", "user", "x y", "k&v", "q=1", "€", "æ", "ключ", "ß", "tag", "z", "ä/ö", "~t", "*p"]
STR_ALPH = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~ !\"#$%&'()*+,/:;<=>?@[\\]^`{|}" \
    "äöüßæéñ€✓☺א日本語漢字𐐷😀"


def rstr(rng, n):
    return "".join(rng.choice(STR_ALPH) for _ in range(rng.randint(0, n)))


def rkey(rng):
    k = rng.choice(KEY_PARTS)
    if rng.random() < 0.5:
        k += str(rng.randint(0, 99))
    return k


def leaf(rng):
    r = rng.random()
    if r < 0.45:
        return rstr(rng, 24)
    if r < 0.6:
        return rng.randint(-10**6, 10**6)
    if r < 0.65:
        return round(rng.uniform(-1000, 1000), 3)
    if r < 0.7:
        return rng.choice([True, False])
    if r < 0.78:
        return None
    if r < 0.82:
        return {"$undef": 1}
    if r < 0.88:
        return {"$date": rng.randint(0, 2 * 10**12)}
    if r < 0.94:
        return {"$buf": rstr(rng, 12)}
    if r < 0.97:
        return {"$sym": rstr(rng, 6)}
    return ""


def split(rng, budget, k):
    """Split `budget` leaves into k positive parts."""
    cuts = sorted(rng.sample(range(1, budget), k - 1)) if k > 1 else []
    return [b - a for a, b in zip([0] + cuts, cuts + [budget])]


def container(rng, budget, as_list):
    k = rng.randint(1, min(budget, 9))
    kids = [value(rng, b) for b in split(rng, budget, k)]
    if as_list:
        return kids
    out = {}
    for v in kids:
        key = rkey(rng)
        while key in out:
            key += "_"
        out[key] = v
    return out


def value(rng, budget):
    if budget <= 1:
        return leaf(rng) if rng.random() < 0.9 else rng.choice([{}, []])
    return container(rng, budget, rng.random() < 0.3)


def rand_opts(rng, obj):
    if rng.random() < 0.15:
        return None
    o = {}
    r = rng.random()
    if r < 0.6:
        o["arrayFormat"] = rng.choice(["indices", "brackets", "repeat", "comma"])
    elif r < 0.75:
        o["indices"] = rng.choice([True, False])
    for name, p in [("allowDots", 0.3), ("strictNullHandling", 0.3), ("skipNulls", 0.25),
                    ("encodeValuesOnly", 0.25), ("addQueryPrefix", 0.2), ("charsetSentinel", 0.15)]:
        if rng.random() < p:
            o[name] = rng.choice([True, True, False])
    if rng.random() < 0.15:
        o["encode"] = False
    if rng.random() < 0.25:
        o["format"] = rng.choice(["RFC1738", "RFC3986"])
    if rng.random() < 0.25:
        o["charset"] = rng.choice(["iso-8859-1", "utf-8"])
    if rng.random() < 0.15:
        o["delimiter"] = rng.choice([";", "&amp;", ","])
    r = rng.random()
    if r < 0.2:
        o["sort"] = {"$fn": rng.choice(["sortAsc", "sortDesc"])}
    elif r < 0.3 and isinstance(obj, dict) and obj:
        keys = list(obj.keys())
        o["filter"] = rng.sample(keys, rng.randint(0, len(keys))) + [rng.randint(0, 3) for _ in range(rng.randint(0, 3))]
    elif r < 0.4:
        o["filter"] = {"$fn": rng.choice(["filterDatesToMs", "filterDropEveryThird", "filterIdentity"])}
    if rng.random() < 0.15:
        o["serializeDate"] = {"$fn": rng.choice(["dateMs7", "dateNull"])}
    if rng.random() < 0.2:
        o["encoder"] = {"$fn": rng.choice(["encCase", "encWrap"])}
    return o


FIXED = [
    ({"a": "b"}, None), ({"a": 1, "b": 2}, None), ({"a": "€", "b": "", "c": "א", "d": "𐐷"}, None),
    ({"$undef": 1}, None), (None, None), (False, None), (0, None), ("", None), ({"$sym": "s"}, None),
    ([{"$sym": "it"}], None), ({}, {"addQueryPrefix": True}), ({"a": "b"}, {"addQueryPrefix": True}),
    ({"a": {"b": {"c": None}}}, {"strictNullHandling": True}), ({"a": {"b": {"c": False}}}, None),
    ({"a": {"b": {"c": {"d": "e"}}}}, {"allowDots": True}),
    ({"a": ["b", "c", "d"]}, {"arrayFormat": "comma"}), ({"a": ["b", "c", "d"]}, {"indices": False}),
    ({"a": {"b": ["c", "d"]}}, {"allowDots": True, "encode": False, "arrayFormat": "comma"}),
    ({"a": [{"b": {"c": [1]}}]}, {"allowDots": True, "encode": False, "arrayFormat": "brackets"}),
    ({"a": [{"b": 1}, 2, 3]}, {"encode": False, "arrayFormat": "brackets"}),
    ({"a": [{"b": "c"}]}, {"indices": False}), ({"a": [], "b": [[]], "c": {}}, {"arrayFormat": "comma"}),
    ({"a": None, "b": ""}, {"strictNullHandling": True}), ({"a": {"b": {"$undef": 1}, "c": None}}, None),
    ({"a": {"$date": 1257894000000}}, None), ({"a": {"$date": 6}}, {"serializeDate": {"$fn": "dateMs7"}}),
    ({"key": {"$date": 6}}, {"strictNullHandling": True, "serializeDate": {"$fn": "dateNull"}}),
    ({"my weird field": "~q1!2\"'w$5&7/z8)?"}, None), ({"a": {"$buf": "test"}, "b": {"c": {"$buf": "a b"}}}, None),
    ({"a b": {"$buf": "a b"}}, {"format": "RFC1738"}), ({"a": "b", "c": "d"}, {"delimiter": ";"}),
    ({"a": {"b": [1, 2, 3, 4], "c": "d"}, "c": "f"}, {"filter": ["a", "b", 0, 2], "arrayFormat": "brackets"}),
    ({"a": 1}, {"filter": []}),
    ({"a": "b", "c": "d", "e": {"f": {"$date": 1257894000000}}}, {"filter": {"$fn": "filterDatesToMs"}}),
    ({"a": "c", "z": {"j": "a", "i": "b"}, "b": "f"}, {"sort": {"$fn": "sortAsc"}}),
    ({"a": "b", "c": ["d", "e=f"], "f": [["g"], ["h"]]}, {"encodeValuesOnly": True}),
    ({"a": {"b": None}}, {"encodeValuesOnly": True, "strictNullHandling": True}),
    ({"æ": "æ", "a": "☺", "b": "𐐷"}, {"charset": "iso-8859-1", "charsetSentinel": True}),
    ({"a": "æ"}, {"charsetSentinel": True, "charset": "utf-8"}),
    ({"KeY": "vAlUe"}, {"encoder": {"$fn": "encCase"}}), ({"a b": None, "c": {"d e": None}}, {"strictNullHandling": True, "format": "RFC1738"}),
    ({"key": None}, {"strictNullHandling": True, "filter": {"$fn": "filterIdentity"}}),
    ({"a": "b c"}, {"encoder": "string"}), ({"a": "b"}, {"charset": "foobar"}), ({"a": "b"}, {"format": "UFO1234"}),
    ({"a": "b"}, {"format": None}), ({"a": "b"}, {"charset": ""}), ({"a": "b"}, {"encoder": None}),
]


def cases(n, mean_leaves, rng, with_fixed):
    out = [{"obj": o, "opts": p} for o, p in FIXED] if with_fixed else []
    for _ in range(n):
        budget = rng.randint(max(1, mean_leaves // 2), mean_leaves * 3 // 2)
        obj = container(rng, budget, rng.random() < 0.08)
        out.append({"obj": obj, "opts": rand_opts(rng, obj)})
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, m)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        data = cases(n, m, rng, size == "S")
        (out_dir / f"workload_{size}.json").write_text(json.dumps(data, ensure_ascii=False))
