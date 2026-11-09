"""Seeded workload generator for isEmail(str, options). Usage: python3 gen_workload.py <out_dir>

Each case is an argument list [str] or [str, options]. Long strings are encoded as
{"$cat": [...]} / {"$rep": [s, n]} and expanded by the driver.
"""
import json, random, sys
from pathlib import Path

RELEASE = 20191121
# (random cases, display-name / padding scale): mean input length ~35 / ~300 / ~3000 characters
SIZES = {"S": (400, 1), "M": (400, 10), "L": (400, 100)}

OPTS = [None, {}, {"allow_display_name": True}, {"require_display_name": True}, {"allow_utf8_local_part": False},
        {"require_tld": False}, {"allow_ip_domain": True}, {"domain_specific_validation": True},
        {"ignore_max_length": True}, {"allow_display_name": True, "ignore_max_length": True},
        {"allow_display_name": True, "allow_utf8_local_part": False, "allow_ip_domain": True}]

FIXED = [
    "foo@bar.com", "x@x.au", "foo@bar.com.au", "foo+bar@bar.com", "hans.m端ller@test.com", "hans@m端ller.com",
    "test|123@m端ller.com", "test123+ext@gmail.com", "some.name.midd.leNa.me+extension@GoogleMail.com",
    '"foobar"@example.com', '"  foo  m端ller "@example.com', '"foo\\@bar"@example.com', '"  foo  bar  "@example.com',
    "a" * 64 + "@" + "a" * 63 + ".com", "a" * 31 + "@gmail.com", "a" * 30 + "@gmail.com", "test@gmail.com",
    "test.1@gmail.com", "invalidemail@", "invalid.com", "@invalid.com", "foo@bar.com.", "somename@ｇｍａｉｌ.com",
    "foo@bar.co.uk.", "z@co.c", "ｇｍａｉｌｇｍａｉｌｇｍａｉｌｇｍａｉｌｇｍａｉｌ@gmail.com",
    "a" * 64 + "@" + "a" * 251 + ".com", "a" * 65 + "@" + "a" * 250 + ".com", "a" * 64 + "@" + "a" * 64 + ".com",
    "a" * 64 + "@" + "a" * 63 + "." + "a" * 63 + "." + "a" * 63 + "." + "a" * 58 + ".com",
    "test1@invalid.co m", "test12@invalid.co　m", "multiple..dots@stillinvalid.com",
    "test123+invalid! sub_address@gmail.com", "gmail...ignores...dots...@gmail.com", "ends.with.dot.@gmail.com",
    "multiple..dots@gmail.com", 'wrong()[]",:;<>@@gmail.com', '"wrong()[]",:;<>@@gmail.com', "foobar@gmail.com",
    "foo.bar@gmail.com", "foo.bar@googlemail.com", ".foobar@gmail.com", "f.o.o.b.a.r@gmail.com", "fo.obar@GMAIL.COM",
    "FooBar+tag@gmail.com", "foo_bar@gmail.com", "tüst@invalid.com", "Some Name <foo@bar.com>", "Some Name <x@x.au>",
    "Some Name <hans.m端ller@test.com>", "'Foo Bar, Esq'<foo@bar.com>", "Name<some.name@GoogleMail.com>",
    "Name\U0001f353With\U0001f351Emoji<test@aftership.com>", '"<displayNameInBrackets>"<jh@gmail.com>',
    '"\\"quotes\\""<jh@gmail.com>', '"name;"<jh@gmail.com>', '"name;" <jh@gmail.com>', "Some Name <invalidemail@>",
    "Some Name foo@bar.co.uk.>", "Some Name <foo@bar.co.uk.", "Some Name < foo@bar.co.uk >", "Name foo@bar.co.uk",
    "Some Name <some..name@gmail.com>", "Some Name<emoji_in_address\U0001f348@aftership.com>",
    "invisibleCharacter\u001f<jh@gmail.com>", "<displayNameInBrackets><jh@gmail.com>", '\\"quotes\\"<jh@gmail.com>',
    '""quotes""<jh@gmail.com>', "name;<jh@gmail.com>", "    <jh@gmail.com>", '"    "<jh@gmail.com>',
    "Some Name  <foo@bar.com>", "a.b <foo@bar.com>", '"a.b" <foo@bar.com>', '"a"b" <foo@bar.com>',
    "email@[123.123.123.123]", "email@255.255.255.255", "email@0.0.0.256", "email@26.0.0.256",
    "email@[266.266.266.266]", "email@[::1]", "email@[]", "email@[1.2.3.4", "email@localhost", "user@host_name.com",
    '"@example.com', '""@example.com', '"a\\"b"@example.com', '"a"b"@example.com', "a@b@c.com", "@", "", "a",
    "foo@bar.com\n", "foo@bar.c0m", "foo@xn--p1ai.xn--p1ai", "user@sub.example.co.uk", "user.@example.com",
    "us er@example.com", "user!#$%&'*+-/=?^_`{|}~@example.com", "a" * 65 + "@b.com", "é" * 33 + "@b.com",
]

LOCAL = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&'*+-/=?^_`{|}~"
UTF = "äöüßéñ端日本語"
DOMAINS = ["example.com", "gmail.com", "googlemail.com", "GMAIL.com", "mail.example.co.uk", "m端ller.com",
           "xn--froschgrn-x9a.com", "co.c", "bad_host.com", "foo.bar.", "-x.com", "[1.2.3.4]", "10.0.0.1",
           "[::ffff:1.2.3.4]", "localhost", "ex ample.com"]
NAMES = ["Some Name", "John Q. Public", '"John Q. Public"', "'Foo Bar, Esq'", '"a \\"b\\" c"', "   ", "x;y",
         "Ünïcødé Nàme", "日本 語", '"<b>"', "name\u0007"]


def rlocal(rng, maxlen):
    parts = []
    for _ in range(rng.randint(1, 4)):
        alpha = LOCAL if rng.random() < 0.85 else LOCAL[:26] + UTF
        parts.append("".join(rng.choice(alpha) for _ in range(rng.randint(1, maxlen))))
    s = ".".join(parts)
    r = rng.random()
    if r < 0.08:
        s = '"' + s.replace('"', '\\"') + ' x"'
    elif r < 0.12:
        s = s + ".."
    return s


def rdomain(rng, k):
    if rng.random() < 0.7:
        return rng.choice(DOMAINS)
    labs = ["".join(rng.choice("abcdefghijklmnop0123-") for _ in range(rng.randint(1, 10))).strip("-") or "a"
            for _ in range(rng.randint(1, 3 * k))]
    return ".".join(labs + [rng.choice(["com", "org", "io", "c"])])


def case(rng, k):
    o = rng.choice(OPTS)
    addr = rlocal(rng, 4 + 2 * min(k, 10)) + "@" + rdomain(rng, k)
    r = rng.random()
    if r < 0.4:
        name = rng.choice(NAMES)
        pad = "".join(rng.choice("abcdefgh ,'") for _ in range(rng.randint(5, 30)))
        if name.startswith('"'):
            s = {"$cat": ['"', {"$rep": [pad, k]}, name[1:], " <", addr, ">"]}
        else:
            s = {"$cat": [{"$rep": [pad, k]}, name, rng.choice(["<", " <"]), addr, ">"]}
        if o is None or not (o.get("allow_display_name") or o.get("require_display_name")):
            o = rng.choice([{"allow_display_name": True}, {"require_display_name": True},
                            {"allow_display_name": True, "ignore_max_length": True}])
    elif r < 0.55 and k > 1:
        s = {"$cat": [{"$rep": [rng.choice(["ab", "a.b", "é"]), 5 * k]}, "@", rdomain(rng, 1)]}
        o = {"ignore_max_length": True}
    else:
        s = addr
    return [s] if o is None else [s, dict(o)]


def cases(n, k, rng, with_fixed):
    out = []
    if with_fixed:
        for s in FIXED:
            for o in OPTS:
                out.append([s] if o is None else [s, dict(o)])
        out += [[None], [42], [["a@b.com"]]]
    out += [case(rng, k) for _ in range(n)]
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, k)) in enumerate(SIZES.items()):
        rng = random.Random(RELEASE + i)
        (out_dir / f"workload_{size}.json").write_text(json.dumps(cases(n, k, rng, size == "S")))
