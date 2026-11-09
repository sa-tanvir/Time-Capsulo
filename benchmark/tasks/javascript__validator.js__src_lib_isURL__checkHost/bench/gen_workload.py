"""Seeded workload generator for checkHost(host, matches). Usage: python3 gen_workload.py <out_dir>

Each case is [host, matches]; regular expressions are encoded as {"$re": [source, flags]}.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20191121
# (cases, list length range): ~10 / ~100 / ~1000 entries per list
SIZES = {"S": (300, (0, 20)), "M": (300, (50, 150)), "L": (300, (600, 1400))}

WORDS = ["foo", "bar", "qux", "cdn", "images", "api", "mail", "static", "a", "b", "c", "example", "test", "xn--p1ai"]
TLDS = ["com", "org", "net", "io", "co.uk"]

FIXED = [
    (["foo.com", "bar.com"], ["http://bar.com/", "bar.com", "foo.com", "foobar.com", "foo.bar.com", "qux.com", "FOO.com", ""]),
    (["bar.com", "foo.com", {"$re": ["\\.foo\\.com$", ""]}],
     ["bar.com", "foo.com", "images.foo.com", "cdn.foo.com", "a.b.c.foo.com", "foobar.com", "foo.bar.com", "qux.com"]),
    ([], ["foo.com", ""]),
    ([{"$re": ["^cdn\\d*\\.", "i"]}, {"$re": ["example", ""]}], ["CDN7.x.com", "cdn.y", "my-example.org", "exam.ple"]),
    (["::1", {"$re": ["^fe80:", ""]}], ["::1", "fe80::1", "::2"]),
]


def host(rng):
    n = rng.randint(1, 4)
    return ".".join(rng.choice(WORDS) + (str(rng.randint(0, 99)) if rng.random() < 0.3 else "") for _ in range(n)) \
        + "." + rng.choice(TLDS)


def entry(rng):
    if rng.random() < 0.85:
        return host(rng)
    w = rng.choice(WORDS)
    pat = rng.choice(["\\.%s\\.com$" % w, "^%s\\d+\\." % w, "%s" % w + str(rng.randint(100, 999)), "^%s$" % host(rng).replace(".", "\\.")])
    return {"$re": [pat, rng.choice(["", "", "i"])]}


def cases(n, lens, rng, with_fixed):
    out = []
    if with_fixed:
        for m, hosts in FIXED:
            out += [[h, m] for h in hosts]
    for _ in range(n):
        m = [entry(rng) for _ in range(rng.randint(*lens))]
        r = rng.random()
        if r < 0.3 and m:
            e = rng.choice(m)
            h = e if isinstance(e, str) else host(rng)
        elif r < 0.4:
            h = host(rng).upper()
        else:
            h = host(rng)
        out.append([h, m])
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, lens)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, lens, rng, size == "S")))
