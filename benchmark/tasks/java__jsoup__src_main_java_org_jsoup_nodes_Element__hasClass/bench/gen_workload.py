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
VOC = ["btn", "Btn-Primary", "x1", "nav", "NAV-item", "a", "ab", "abc", "col-md-6", "Foo_Bar", "é", "ÉCOLE", "highlight", "hl", "container-fluid", "row", "item0", "item10", "active", "disabled"]
SEPS = [" ", " ", "  ", "\t", "\n", "\f", "\r", " \t "]
SIZES = {"S": (8, 30, 12), "M": (3, 3000, 70), "L": (3, 300000, 60)}

def mk(rng, n):
    s = ""
    while len(s) < n:
        s += rng.choice(VOC) + rng.choice(SEPS)
    s = s[:n]
    return s

def queries(rng, attr, k):
    toks = [t for t in attr.replace("\t", " ").replace("\n", " ").replace("\f", " ").replace("\r", " ").split(" ") if t]
    qs = []
    for _ in range(k):
        r = rng.random()
        if r < 0.3 and toks:
            t = rng.choice(toks)
            qs.append(t.swapcase() if rng.random() < 0.5 else t)
        elif r < 0.5 and toks:
            t = rng.choice(toks)
            qs.append(t[: max(1, len(t) - 1)])
        elif r < 0.65 and toks:
            t = rng.choice(toks)
            qs.append(t[1:] or "q")
        elif r < 0.7:
            qs.append("")
        elif r < 0.8:
            qs.append(rng.choice(VOC) + "zz")
        else:
            qs.append("zz" + str(rng.randint(0, 99999)))
    return qs

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        ne, ln, nq = SIZES[size]
        rows = []
        if size == "S":
            rows += ["E\tclass\t", "Q\tfoo", "Q\t",
                     "E\tclass\tfoo", "Q\tfoo", "Q\tFOO", "Q\tfo", "Q\tfooo",
                     "E\tCLASS\t  foo  ", "Q\tfoo", "Q\tbar",
                     "E\tclass\tfoo bar", "Q\tbar", "Q\tBAR", "Q\tfoo", "Q\tbaz",
                     "E\tclass\t\\tfoo\\nbar\\f", "Q\tbar", "Q\tfoo",
                     "E\tclass\tfoobar foo", "Q\tfoo", "Q\tfoobar", "Q\too",
                     "E\tclass\tÉcole x".replace("É", "\\u00c9"), "Q\t\\u00e9cole", "Q\tx"]
            rows.append("E\tnone\t")
            rows += ["Q\tfoo"]
        for _ in range(ne):
            attr = mk(rng, rng.randint(ln // 2, ln))
            key = rng.choice(["class", "class", "CLASS", "Class"])
            rows.append("E\t%s\t%s" % (key, esc(attr)))
            for q in queries(rng, attr, nq):
                rows.append("Q\t" + esc(q))
        write(out, size, rows)

main(sys.argv[1])
