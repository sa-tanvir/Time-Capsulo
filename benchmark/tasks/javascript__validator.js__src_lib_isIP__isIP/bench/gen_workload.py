"""Seeded workload generator for isIP(str, version). Usage: python3 gen_workload.py <out_dir>

Each case is an argument list [str] or [str, version]. Long strings are encoded as
{"$cat": [...]} / {"$rep": [s, n]} and expanded by the driver.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20191121
# (random cases, scale of zone ids / junk runs): mean input length ~20 / ~200 / ~2000 characters
SIZES = {"S": (400, 1), "M": (400, 10), "L": (400, 100)}

VERSIONS = [None, None, None, 4, 6, "4", "6", "", 10]
HEX = "0123456789abcdefABCDEF"

FIXED = [
    "127.0.0.1", "0.0.0.0", "255.255.255.255", "1.2.3.4", "::1", "2001:db8:0000:1:1:1:1:1", "2001:41d0:2:a141::1",
    "::ffff:127.0.0.1", "::0000", "0000::", "1::", "1111:1:1:1:1:1:1:1", "fe80::a6db:30ff:fe98:e946", "::",
    "0:0:0:0:0:ffff:127.0.0.1", "abc", "256.0.0.0", "0.0.0.256", "26.0.0.256", "0200.200.200.200",
    "200.0200.200.200", "200.200.200.0200", "::banana", "banana::", "::1banana", "::1::", "1:", ":1", ":1:1:1::2",
    "1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1", "::11111", "11111:1:1:1:1:1:1:1", "2001:db8:0000:1:1:1:1::1",
    "0:0:0:0:0:0:ffff:127.0.0.1", "0:0:0:0:ffff:127.0.0.1", "fe80::1234%1", "ff08::9abc%10", "ff08::9abc%interface10",
    "ff02::5678%pvc1.3", "::ffff:287.0.0.1", "%", "fe80::1234%", "fe80::1234%1%3%4", "fe80%fe80%", "", "1.2.3",
    "1.2.3.4.5", "01.02.03.004", "1.2.3.4 ", " 1.2.3.4", "1.2.3.-4", "1:2:3:4:5:6:7:8", "1:2:3:4:5:6:7::",
    "::1:2:3:4:5:6:7", "1:2:3::4:5:6:7", "1::2::3", ":::", "1:::2", "::2:", "::1.2.3.4", "1::1.2.3.4",
    "1:2:3:4:5:6:1.2.3.4", "1:2:3:4:5:6:7:1.2.3.4", "::1.2.3", "fe80::%1", "fe80::1%eth0", "1.2.3.4%1", "%1",
    "FFFF::abcd", "g::1", "12345::", "1:2:3:4:5:6:7:8:9", "1.2.3.4::", "::256.1.1.1", "１.２.３.４", "1.2.3.٤",
]


def ipv4(rng):
    return ".".join(str(rng.choice([rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 999)])) for _ in range(4))


def block(rng):
    return "".join(rng.choice(HEX) for _ in range(rng.choice([1, 2, 3, 4, 4, 4, 5])))


def ipv6(rng):
    n = rng.choice([8, 8, 6, 7, 9])
    blocks = [block(rng) for _ in range(n)]
    if rng.random() < 0.2:
        blocks[-1] = ipv4(rng)
    if rng.random() < 0.5:
        i = rng.randrange(len(blocks))
        j = min(len(blocks), i + rng.randint(1, 4))
        blocks[i:j] = [""] if 0 < i < len(blocks) - 1 else ["", ""]
    s = ":".join(blocks)
    if rng.random() < 0.05:
        s = s.replace(":", ":::", 1)
    return s


def zone(rng, k):
    return "".join(rng.choice("abcdefghij0123456789.") for _ in range(rng.randint(1, 8))) * rng.randint(1, k)


def case(rng, k):
    r = rng.random()
    if r < 0.25:
        s = ipv4(rng)
        if rng.random() < 0.3:
            s = {"$cat": [s, {"$rep": ["0", rng.randint(1, 10 * k)]}]}
    elif r < 0.6:
        s = ipv6(rng)
        if rng.random() < 0.6:
            s = {"$cat": [s, "%", zone(rng, 10 * k)]}
    elif r < 0.8:
        s = {"$cat": [{"$rep": [block(rng) + ":", rng.randint(2, 20 * k)]}, block(rng)]}
    else:
        s = {"$rep": [rng.choice(["1.", "ab", "a:", "::", "%x", "1.2.3.4"]), rng.randint(1, 20 * k)]}
    v = rng.choice(VERSIONS)
    return [s] if v is None else [s, v]


def cases(n, k, rng, with_fixed):
    out = []
    if with_fixed:
        for s in FIXED:
            for v in VERSIONS[2:]:
                out.append([s] if v is None else [s, v])
        out += [["::1", 0], ["::1", None], ["1.2.3.4", 4.0], [12345], [None]]
    out += [case(rng, k) for _ in range(n)]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, k, rng, size == "S")))
