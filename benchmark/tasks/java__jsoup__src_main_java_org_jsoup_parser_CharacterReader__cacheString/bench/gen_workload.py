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
# size -> (buffer chars, calls, vocabulary size)
SIZES = {"S": (300, 80, 25), "M": (30000, 20000, 400), "L": (300000, 300000, 3000)}

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        bl, nc, nv = SIZES[size]
        vocab = ["".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 12, 13, 14, 16, 20]))) for _ in range(nv)]
        words = []
        buf = ""
        while len(buf) < bl:
            w = rng.choice(vocab)
            words.append((len(buf), len(w)))
            buf += w + " "
        buf = buf[:bl]
        words = [(s, c) for s, c in words if s + c <= len(buf)]
        rows = [esc(buf)]
        if size == "S":
            rows += ["0\t0\t1", "5\t0\t2", "0\t1\t2", "0\t12\t2", "0\t13\t2", "0\t14\t1", "3\t-1\t2", "%d\t5\t2" % (len(buf) - 5)]
        while len(rows) - 1 < nc:
            r = rng.random()
            if r < 0.8:
                s, c = rng.choice(words)
            elif r < 0.9:
                c = rng.randint(1, 30)
                s = rng.randint(0, len(buf) - c)
            elif r < 0.95:
                s = rng.randint(0, len(buf))
                c = 0
            else:
                s, c = rng.choice(words)
                s, c = s, min(c + rng.randint(1, 20), len(buf) - s)
            rows.append("%d\t%d\t%d" % (s, c, 2 if rng.random() < 0.3 else 1))
        write(out, size, rows)

main(sys.argv[1])
