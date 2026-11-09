import random, sys, os
SAFE = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,:;<>=/!?-_#()[]{}'\"*+~^$|&@%")

def esc(s):
    """ASCII-only, single-line encoding: \\t \\n \\f \\r \\\\ and \\uXXXX per UTF-16 unit."""
    out = []
    u = s.encode("utf-16-le", "surrogatepass")
    for i in range(0, len(u), 2):
        w = u[i] | (u[i + 1] << 8)
        ch = chr(w)
        if ch in SAFE:
            out.append(ch)
        elif ch == "\t": out.append("\\t")
        elif ch == "\n": out.append("\\n")
        elif ch == "\f": out.append("\\f")
        elif ch == "\r": out.append("\\r")
        elif ch == "\\": out.append("\\\\")
        else: out.append("\\u%04x" % w)
    return "".join(out)

def write(out, size, lines):
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

SEED = 20190513
# size -> (cases, text chars per case)
SIZES = {"S": (70, 8), "M": (40, 3000), "L": (6, 250000)}

def enc_text(rng, n, hi):
    out = bytearray()
    for _ in range(n):
        r = rng.random()
        if r < 1 - hi: cp = rng.randint(32, 126)
        elif r < 1 - hi * 0.6: cp = rng.randint(0x80, 0x7ff)
        elif r < 1 - hi * 0.2: cp = rng.randint(0x800, 0xd7ff)
        else: cp = rng.randint(0x10000, 0x10ffff)
        out += chr(cp).encode("utf-8")
    return out

def mutate(rng, b):
    b = bytearray(b)
    k = rng.randint(0, 7)
    if not b: return bytes([0xC3])
    if k == 0: b = b[:-1] if b[-1] >= 0x80 else b + bytes([0xE2, 0x82])
    elif k == 1: b[rng.randrange(len(b))] = 0xFF
    elif k == 2: b[rng.randrange(len(b))] = 0x80 + rng.randrange(64)
    elif k == 3: b += bytes([0xF8, 0x88, 0x80, 0x80, 0x80])
    elif k == 4: b += bytes([0xC3])
    elif k == 5: b += bytes([0xF0, 0x9F, 0x98])
    elif k == 6: b[rng.randrange(len(b))] = 0xC3
    else: b = bytes([0xEF, 0xBB]) + b
    return bytes(b)

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        nc, ln = SIZES[size]
        rows = []
        if size == "S":
            fixed = [b"", b"a", b"\xef\xbb\xbf", b"\xef\xbb\xbfA", b"\xef\xbb", b"\xc3\xa9", b"\xc3", b"\xc3\xa9\xc3", b"\xe2\x82\xac", b"\xe2\x82", b"\xe2\x82\xacx",
                     b"\xf0\x9f\x98\x80", b"\xf0\x9f\x98", b"\xf0\x9f\x98\x80!", b"\xff", b"\x80", b"\xc3\x28", b"\xe2\x28\xa1", b"\xf8\x88\x80\x80\x80", b"A\xc3\xa9B", b"\xc3\xa9\xef\xbb\xbf",
                     b"\xef\xbb\xbf\xc3\xa9", b"\xef\xbb\xbf\xc3", b"abc\xe9", b"caf\xe9 au lait"]
            rows += ["H\t" + x.hex() for x in fixed]
        while len(rows) < nc:
            hi = rng.choice([0.0, 0.1, 0.5, 0.9])
            b = bytes(enc_text(rng, rng.randint(max(1, ln // 2), ln), hi))
            if rng.random() < 0.2: b = b"\xef\xbb\xbf" + b
            if rng.random() < 0.4: b = mutate(rng, b) if size == "S" else (b + mutate(rng, b[-6:]) if rng.random() < 0.6 else b[: len(b) // 2] + mutate(rng, b[len(b) // 2: len(b) // 2 + 4]) + b[len(b) // 2 + 4:])
            rows.append("H\t" + b.hex())
        write(out, size, rows)

main(sys.argv[1])
