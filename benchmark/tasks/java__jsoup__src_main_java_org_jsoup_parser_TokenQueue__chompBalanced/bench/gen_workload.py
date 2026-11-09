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
SIZES = {"S": (70, 30, 3), "M": (150, 2000, 12), "L": (24, 100000, 40)}
WORDS = ["a", "bc", "foo", "x y", "1,2", "id", "=", "z", " "]
PAIRS = [("(", ")"), ("[", "]"), ("{", "}"), ("<", ">")]

def body(rng, n, depth, o, c):
    parts = []
    size = 0
    while size < n:
        r = rng.random()
        if r < 0.55: t = rng.choice(WORDS)
        elif r < 0.65: t = "'" + rng.choice(["q", o, c, "a b", '"']) + "'"
        elif r < 0.72: t = '"' + rng.choice(["q", o, c, "a b", "'"]) + '"'
        elif r < 0.8: t = "\\" + rng.choice([o, c, "x", "\\"])
        elif depth > 0 and n > 20:
            t = o + body(rng, rng.randint(1, max(1, n // 4)), depth - 1, o, c) + c
        else: t = rng.choice(WORDS)
        parts.append(t)
        size += len(t)
    return "".join(parts)

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        nc, ln, dp = SIZES[size]
        rows = []
        if size == "S":
            for s in ["(one (two) three) four", "(one (two) \\( \\) \\) three) four", "(something(or another)) else", "abc", "", "(", ")", "()", "(()", "((a)", "x(a)",
                      "(a 'b)' c) d", "(a \"b)\" c) d", "('a) b", "(a \\) b", "(\\(a) b", "'(a)", "(a)(b)", "((((a))))z", "(a'b)c'd)e"]:
                rows.append("(\t)\t" + esc(s))
            for s in ["[a[b]c]d", "[a ']' b]c", "{a{b}c}d", "<a<b>c>d", "[a(b]c)", "[[x]"]:
                o, c = {"[": ("[", "]"), "{": ("{", "}"), "<": ("<", ">")}[s[0]]
                rows.append("%s\t%s\t%s" % (o, c, esc(s)))
        while len(rows) < nc:
            o, c = rng.choice(PAIRS)
            inner = body(rng, rng.randint(max(1, ln // 2), ln), dp, o, c)
            s = o + inner + c + rng.choice(["", " tail", ")x"])
            r = rng.random()
            if r < 0.12: s = s[: max(1, len(s) // 2)]
            elif r < 0.2: s = rng.choice(["x", "ab "]) + s
            elif r < 0.25 and size == "S": s = s[:-1]
            rows.append("%s\t%s\t%s" % (esc(o), esc(c), esc(s)))
        write(out, size, rows)

main(sys.argv[1])
