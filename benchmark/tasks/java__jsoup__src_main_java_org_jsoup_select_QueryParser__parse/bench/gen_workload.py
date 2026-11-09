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
SIZES = {"S": (60, 3), "M": (60, 40), "L": (30, 250)}
TAGS = ["div", "p", "a", "span", "ul", "li", "b", "section", "h1"]
SIMPLE = ["{t}", ".{c}", "#{i}", "{t}.{c}", "{t}#{i}", "[href]", "[class]", "{t}[href^=http]", "a[href$=.pdf]", "[data-x*=ab]", "{t}[id=a1]", "[title~=hello]",
          "[class!=zz]", "*", "{t}:first-child", "{t}:last-child", "{t}:nth-child(2n+1)", "li:nth-last-child(2)", "{t}:nth-of-type(odd)", "{t}:only-child", "{t}:empty", "{t}:eq(1)", "{t}:lt(2)",
          "{t}:gt(0)", "{t}:contains(foo bar)", "{t}:containsOwn(one (two))", "{t}:matches(\\\\d+)", "{t}:not(.{c})", "{t}:has(a)", "{t}:has(> p)", "{t}[href=\"x y\"]", "ns|{t}", "{t}:first-of-type", "[^data-]"]
COMB = [" ", " > ", " + ", " ~ ", ", ", ">", ",", "+", "~"]
BAD = ["a[href=\"]", "p:contains(One \" One)", "", "a >", ":nth-child(x)", "a[", "div:not(", "!!", "a, ", "p:contains(unclosed", "[=x]", ">", "> a", "+ p", "~ a, b", ", a"]

def simple(rng):
    return rng.choice(SIMPLE).format(t=rng.choice(TAGS), c=rng.choice(["c1", "c2", "c3", "foo"]), i=rng.choice(["a1", "b2", "id3"]))

def query(rng, parts, combs):
    q = simple(rng)
    for _ in range(parts):
        q += rng.choice(combs) + simple(rng)
        if rng.random() < 0.3:
            q += simple(rng).replace("*", "")
    return q

def doc(rng, n):
    h = ["<html><head><title>t</title></head><body>"]
    depth = 0
    for k in range(n):
        t = rng.choice(TAGS)
        attr = ""
        if rng.random() < 0.5: attr += ' class="%s"' % rng.choice(["c1", "c2 c3", "foo", "c1 foo"])
        if rng.random() < 0.3: attr += ' id="%s"' % rng.choice(["a1", "b2", "id3"])
        if rng.random() < 0.2: attr += ' href="%s"' % rng.choice(["http://x/a.pdf", "x y", "/p"])
        h.append("<%s%s>%s" % (t, attr, rng.choice(["foo bar", "one (two)", "123", ""])))
        if rng.random() < 0.5: h.append("</%s>" % t)
    h.append("</body></html>")
    return "".join(h)

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        nq, parts = SIZES[size]
        rows = ["D\t" + esc(doc(rng, {"S": 40, "M": 300, "L": 600}[size]))]
        if size == "S":
            for q in ["a b, c d, e f", ".foo > ol, ol > li + li", "div > p", "a ~ b + c", "  p  ", "p,a", "p , a", "p>a", "p>>a", "p, , a", "a:not(b c)", "p:has(a, b)", "div p, ul > li:first-child", "div:has(p) > a", "p.c1.foo", "p[class=c1]:not(.c2) a"] + BAD:
                rows.append("Q\t" + esc(q))
        while len(rows) - 1 < nq:
            if size == "S" and rng.random() < 0.15:
                q = rng.choice(BAD)
            else:
                combs = COMB if rng.random() < 0.7 else [" ", ", "]
                p = rng.randint(0, parts) if size != "L" or rng.random() < 0.3 else rng.randint(parts // 2, parts)
                q = query(rng, p, combs)
                if size == "L" and rng.random() < 0.5:
                    q = query(rng, rng.randint(150, 400), [", "])
            rows.append("Q\t" + esc(q))
        write(out, size, rows)

main(sys.argv[1])
