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
SIZES = {"S": (60, 40), "M": (100, 3000), "L": (12, 250000)}
CH = ["a", "b", "Z", "x", "é", "1", "-", ".", "\U0001F600", "\U0001D504", "中"]
WS = [" ", " ", " ", "\t", "\n", "\f", "\r", " "]
INV = ["​", "‌", "‍", "­"]
OTHER_WS = [" ", "\u000b", "\u0085"]  # not whitespace for this function

def gen(rng, n):
    p = rng.random() * 0.6 + 0.1
    out = []
    for _ in range(n):
        r = rng.random()
        if r < p * 0.8: out.append(rng.choice(WS))
        elif r < p * 0.9: out.append(rng.choice(INV))
        elif r < p * 0.92: out.append(rng.choice(OTHER_WS))
        else: out.append(rng.choice(CH))
    return "".join(out)

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        nc, ln = SIZES[size]
        rows = []
        if size == "S":
            fixed = ["", " ", "   ", "a", " a", "a ", " a ", "a   b", "\t\n a \r\f b   c", "​ ​", "a​ b", "a ​ b",
                     "­", "x  y", "\U0001F600 \U0001F600", "a b", "  ‍  a"]
            for s in fixed:
                rows.append("%d\t%s" % (rng.randint(0, 1), esc(s)))
        while len(rows) < nc:
            rows.append("%d\t%s" % (rng.randint(0, 1), esc(gen(rng, rng.randint(max(1, ln // 2), ln)))))
        write(out, size, rows)

main(sys.argv[1])
