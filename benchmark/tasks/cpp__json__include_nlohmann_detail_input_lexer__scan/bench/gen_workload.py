"""Seeded workload generator for lexer::scan. Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <input bytes as lowercase hex>.  The driver calls scan() repeatedly until end_of_input or parse_error,
recording the token kinds, values and positions.
S: hand-written inputs (every token kind, all whitespace characters, BOM variants, NUL and other control bytes, literal prefixes, bad characters, numbers, strings with escapes)
plus random small JSON documents with random whitespace; M/L: pretty-printed / compact random JSON documents of about 3 * 10^4 / 4 * 10^5 bytes each.
"""
import json, random, sys
from pathlib import Path

WS = [" ", "\t", "\n", "\r"]


def scalar(rng):
    t = rng.randrange(8)
    if t == 0: return None
    if t == 1: return rng.random() < 0.5
    if t == 2: return rng.randrange(-1000, 1000)
    if t == 3: return rng.randrange(0, 2 ** 64)
    if t == 4: return rng.randrange(-2 ** 63, 0)
    if t == 5: return rng.randrange(-10 ** 6, 10 ** 6) / 64.0
    if t == 6: return "".join(rng.choice("abcdefghij \u00e9\u20ac\"\\\n/") for _ in range(rng.randrange(0, 14)))
    return rng.randrange(-10 ** 9, 10 ** 9) * 10.0 ** rng.randrange(-5, 12)


def gen(rng, depth, budget):
    if depth == 0 or budget <= 1 or rng.random() < 0.3:
        return scalar(rng)
    n = rng.randrange(0, 8)
    share = max(1, budget // max(n, 1))
    if rng.random() < 0.5:
        return [gen(rng, depth - 1, share) for _ in range(n)]
    return {"key%d" % rng.randrange(1000): gen(rng, depth - 1, share) for _ in range(n)}


def with_ws(rng, text):
    """insert random JSON whitespace between tokens (outside strings)"""
    out, i, instr = [], 0, False
    while i < len(text):
        c = text[i]
        out.append(c)
        if instr:
            if c == "\\":
                i += 1
                out.append(text[i])
            elif c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c in "[]{},:" and rng.random() < 0.3:
            out.append("".join(rng.choice(WS) for _ in range(rng.randrange(1, 4))))
        i += 1
    return "".join(out)


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for size in "SML":
        rng = random.Random(20191111 + "SML".index(size))
        lines = []
        if size == "S":
            raw = [b"", b" ", b"\t\n\r ", b"[", b"]", b"{", b"}", b":", b",", b"[]", b"{}", b"{\"a\":1}", b"[1,2,3]", b"true", b"false", b"null", b"t", b"tru", b"truex", b"true false",
                   b"fals", b"nul", b"nulll", b"nill", b"\"abc\"", b"\"a\\nb\"", b"\"\\u00e9\"", b"\"unterminated", b"\"a\x01\"", b"0", b"-1", b"12", b"1.5", b"-0.5e3", b"1e5", b"123456789012345678901234567890",
                   b"-", b"01", b"1.", b".5", b"+1", b"1e", b"18446744073709551615", b"18446744073709551616", b"-9223372036854775808", b"-9223372036854775809",
                   b"\xef\xbb\xbf[1]", b"\xef\xbb\xbf", b"\xef\xbb", b"\xef", b"\xef\xbb\xbd", b"\xef\xbf\xbf", b"\xbb\xbf[1]", b"[1]\xef\xbb\xbf", b" \xef\xbb\xbf[1]", b"\xef\xbb\xbf\xef\xbb\xbf[1]",
                   b"\x00", b"\x00[1]", b"[1]\x00", b"[1]\x00[2]", b"\x0b", b"\x0c[1]", b"\x1f", b"\x7f", b"\xff", b"\xc3\xa9", b"a", b"#", b"'a'", b"/", b"\\", b"truefalse", b"[true,false,null]",
                   b" [ 1 , 2 ] ", b"\r\n[\r\n1\r\n]\r\n", b"\t{\t\"a\"\t:\t1\t}\t", b"[1,\x0b2]", b"[1,\xc2\xa02]", b"{\"a\" : [ true , null ] , \"b\" : \"x\" }", b"[\"\xff\"]", b"-a", b"1 2", b"1a", b"nulltrue",
                   b"\xef\xbb\xbf\t\n true"]
            for r in raw:
                lines.append("\t".join(["1", r.hex()]))
            for _ in range(20):
                v = gen(rng, 3, 25)
                t = with_ws(rng, json.dumps(v, ensure_ascii=rng.random() < 0.5)).encode()
                r = rng.random()
                if r < 0.15: t = b"\xef\xbb\xbf" + t
                elif r < 0.3: t = t[:rng.randrange(0, len(t) + 1)]
                elif r < 0.4: t = t + b" \x00 " + t
                lines.append("\t".join(["1", t.hex()]))
        else:
            ncase, budget, depth, reps = {"M": (8, 1200, 6, 4), "L": (4, 20000, 8, 1)}[size]
            for c in range(ncase):
                v = [gen(rng, depth, budget) for _ in range(rng.randrange(5, 12))]
                if size == "L":
                    v = [gen(rng, depth, budget) for _ in range(40)]
                text = json.dumps(v, indent=rng.choice([None, 1, 2, 4]), ensure_ascii=(c % 2 == 0))
                if c % 3 == 1:
                    text = with_ws(rng, json.dumps(v))
                lines.append("\t".join([str(reps), text.encode().hex()]))
        (out / ("workload_%s.txt" % size)).write_text("\n".join(lines) + "\n")


main()
