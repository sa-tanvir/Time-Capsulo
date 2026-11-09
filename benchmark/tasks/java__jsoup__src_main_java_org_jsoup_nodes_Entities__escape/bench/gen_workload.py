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
SIZES = {"S": (70, 40), "M": (100, 3000), "L": (12, 250000)}
CHARS = list("abcdefghij KLMNOP") + ["&", "<", ">", "\"", "'", " ", "é", "ü", "©", "€", "中", "Ω", "\U0001F600", "\U0001D504", " ", "\t", "\n", "  ", "—", "ß"]
SETS = [("UTF-8", "base"), ("UTF-8", "xhtml"), ("UTF-8", "extended"), ("US-ASCII", "base"), ("US-ASCII", "xhtml"),
        ("US-ASCII", "extended"), ("ISO-8859-1", "base"), ("ISO-8859-1", "extended"), ("ISO-8859-1", "xhtml")]

def text(rng, n):
    w = [rng.random() for _ in CHARS]
    return "".join(rng.choices(CHARS, weights=[1 + 6 * x for x in w], k=n))

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        nc, ln = SIZES[size]
        rows = []
        if size == "S":
            for cs, md in SETS:
                for fl in ("000", "100", "010", "011", "111"):
                    if len(rows) < 30:
                        rows.append("%s\t%s\t%s\t%s" % (fl, cs, md, esc("a<b>&\"c dé ü\U0001D504\U0001F600  e\n")))
            rows.append("000\tUTF-8\tbase\t")
            rows.append("011\tUTF-8\tbase\t   ")
        while len(rows) < nc:
            cs, md = rng.choice(SETS)
            fl = "".join(rng.choice("01") for _ in range(3))
            rows.append("%s\t%s\t%s\t%s" % (fl, cs, md, esc(text(rng, rng.randint(max(1, ln // 2), ln)))))
        write(out, size, rows)

main(sys.argv[1])
