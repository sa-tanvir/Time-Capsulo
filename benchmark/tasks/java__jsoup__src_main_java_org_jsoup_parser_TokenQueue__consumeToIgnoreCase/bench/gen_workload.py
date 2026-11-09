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
SIZES = {"S": (60, 40, 3), "M": (100, 3000, 4), "L": (30, 200000, 4)}
WORDS = ["foo", "bar ", "Sx", "<p>", "text", "a-b", "  ", "1x ", "<b>", "ss", "SS", "TEXTAREA", "scrip", "<!-", "--"]
SEQS = ["</script", "-->", "</textarea>", "ab", "A", "s", "S", "1x", "<P>", "é", "ss", "--", "x", "</STYLE"]

def mk(rng, n, seqs):
    parts = []
    size = 0
    while size < n:
        t = rng.choice(WORDS)
        parts.append(t)
        size += len(t)
    s = "".join(parts)
    # plant a few occurrences (random case) of the sequences, the last one late in the text
    for q in seqs:
        if rng.random() < 0.8:
            pos = rng.randint(max(0, len(s) - 60), len(s)) if rng.random() < 0.6 else rng.randint(0, len(s))
            qq = "".join(ch.swapcase() if rng.random() < 0.4 else ch for ch in q)
            s = s[:pos] + qq + s[pos:]
    return s

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        nc, ln, ns = SIZES[size]
        rows = []
        if size == "S":
            rows.append("\\u003ctextarea>one < two </TEXTarea> third </TEXTarea>\t</textarea>\t</textarea>".replace("\\u003c", "<"))
            rows.append("<textarea> one two < three </oops>\t</textarea")
            rows.append("abc\tABC\tx")
            rows.append("\tab")
            rows.append("aAbB\tb\tB\tb")
            rows.append("xyz\tz\ty")
            rows.append("1x1X1x\t1X\t1x\t1x")
        while len(rows) < nc:
            seqs = [rng.choice(SEQS) for _ in range(rng.randint(1, ns))]
            s = mk(rng, rng.randint(max(1, ln // 2), ln), seqs)
            rows.append(esc(s) + "\t" + "\t".join(esc(q) for q in seqs))
        write(out, size, rows)

main(sys.argv[1])
