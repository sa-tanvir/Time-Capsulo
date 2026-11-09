"""Seeded workload generator for parse_header_links. Usage: python3 gen_workload.py <out_dir>"""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (300, 4), "M": (300, 40), "L": (300, 400)}   # (cases, max links per header)
URLCH = string.ascii_letters + string.digits + "/:._-?&=%"


def url(rng):
    return "http://" + "".join(rng.choice(URLCH) for _ in range(rng.randint(3, 40)))


def param(rng):
    r = rng.random()
    key = rng.choice(["rel", "type", "title", "anchor", "hreflang", "media", "rev"])
    val = rng.choice(["next", "last", "prev", "first", "image/jpeg", "a, b", "x y", "", "it's"])
    if r < 0.4:
        return f"{key}={val}"
    if r < 0.7:
        return f'{key}="{val}"'
    if r < 0.8:
        return f" {key} = '{val}' "
    if r < 0.86:
        return ""                       # empty piece -> stop
    if r < 0.92:
        return f"{key}={val}=extra"     # two '=' -> stop
    return key                          # no '=' -> stop


def link(rng):
    u = url(rng)
    u = rng.choice([f"<{u}>", f"<{u}>", f" <{u}> ", f"'{u}'", u])
    params = [param(rng) for _ in range(rng.randint(0, 4))]
    if not params:
        return u + rng.choice(["", ";", "; "])
    return u + ";" + ";".join(rng.choice(["", " "]) + p for p in params)


def case(rng, n):
    if rng.random() < 0.03:
        return rng.choice(["", "   ", "\"'\"", " '' "])
    links = [link(rng) for _ in range(rng.randint(1, n))]
    s = links[0]
    for l in links[1:]:
        s += rng.choice([",", ", ", ",   ", " , "]) + l
    return rng.choice(["", " ", '"']) + s + rng.choice(["", " ", '"'])


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, c)) in enumerate(SIZES.items()):
        rng = random.Random(20190822 + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps([case(rng, c) for _ in range(n)]))
