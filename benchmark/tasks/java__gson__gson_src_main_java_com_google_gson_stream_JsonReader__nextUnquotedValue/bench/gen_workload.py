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

SEED = 20191005
CHUNKS = [0, 0, 0, 1, 2, 3, 5, 7, 64, 1000]

def row(chunk, lenient, calls, pre, unit, count, suf):
    # fields: chunk, flag(L=lenient,S=strict), calls, prefix, unit, count, suffix (text = prefix + unit*count + suffix)
    return "\t".join([str(chunk), "L" if lenient else "S", str(calls), esc(pre), esc(unit), str(count), esc(suf)])

SIZES = {"S": (400, 30), "M": (4000, 300), "L": (3000, 12000)}
WORD = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.@!$%^&*()+~`'\"<>?|"
DELIMS = ["{", "}", "[", "]", ":", ",", " ", "\t", "\f", "\r", "\n"]
LENIENT_CH = ["/", "\\", ";", "#", "="]
def gen(rng, size):
    nc, ln = SIZES[size]
    rows = []
    if size == "S":
        for t in ["", "a", "abc ", "abc,", "abc]", "abc}", "abc:", "abc\n", "abc/def", "abc\\def", "abc;def", "abc#def", "abc=def", ",abc", " abc", "/abc", "true", "12ab", "-"]:
            for chunk, lenient in ((0, False), (0, True), (1, True), (3, False)):
                rows.append(row(chunk, lenient, 1, t, "", 0, ""))
    while len(rows) < nc:
        L = rng.randint(max(1, ln // 3), ln)
        unit = "".join(rng.choice(WORD) for _ in range(rng.choice([1, 4, 16, 50])))
        cnt = max(1, L // len(unit))
        r = rng.random()
        pre = "".join(rng.choice(WORD) for _ in range(rng.randint(0, 5)))
        if r < 0.55: suf = rng.choice(DELIMS) + "tail"
        elif r < 0.75: suf = ""
        elif r < 0.9: suf = rng.choice(LENIENT_CH) + "tail"
        else: suf = rng.choice(DELIMS)
        lenient = rng.random() < 0.6
        rows.append(row(rng.choice(CHUNKS), lenient, 1, pre, unit, cnt, suf))
    return rows


def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        write(out, size, gen(rng, size))

main(sys.argv[1])
