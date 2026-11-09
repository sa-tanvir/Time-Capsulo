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
SIZES = {"S": (12, 8), "M": (3, 300), "L": (3, 12000)}
NAMES = ["q", "user", "email", "pw", "opt", "agree", "color", "x", "y", "Name", "a b", "n1", "n2", "t"]
TYPES = ["text", "text", "hidden", "password", "checkbox", "radio", "submit", "file", "image", "reset", "TEXT", "Checkbox", "RADIO", "number", "", None]
VALS = ["", "v", "hello world", "1", "a&b", "<x>", "café", "on", "yes", None]

def attrs(d):
    out = []
    for k, v in d:
        if v is None: continue
        if v is True: out.append(k)
        else: out.append('%s="%s"' % (k, v.replace("&", "&amp;").replace('"', "&quot;")))
    return " ".join(out)

def control(rng):
    r = rng.random()
    nm = rng.choice(NAMES) if rng.random() > 0.12 else rng.choice(["", None])
    dis = True if rng.random() < 0.1 else None
    if r < 0.55:
        t = rng.choice(TYPES)
        return "<input %s>" % attrs([("type", t), ("name", nm), ("value", rng.choice(VALS)), ("checked", True if rng.random() < 0.4 else None), ("disabled", dis)])
    if r < 0.7:
        body = rng.choice(["", "text", "  two\nlines ", "a<b"])
        return "<textarea %s>%s</textarea>" % (attrs([("name", nm), ("disabled", dis)]), body.replace("<", "&lt;"))
    if r < 0.88:
        k = rng.randint(0, 5)
        multi = rng.random() < 0.4
        opts = []
        for j in range(k):
            sel = True if rng.random() < (0.25 if multi else 0.12) else None
            opts.append("<option %s>opt %d</option>" % (attrs([("value", rng.choice(["v%d" % j, "", None])), ("selected", sel)]), j))
        return "<select %s>%s</select>" % (attrs([("name", nm), ("multiple", True if multi else None), ("disabled", dis)]), "".join(opts))
    if r < 0.94:
        return "<button %s>go</button>" % attrs([("name", nm), ("value", "b"), ("type", "submit")])
    if r < 0.97:
        return "<keygen %s>" % attrs([("name", nm)])
    return "<object %s></object>" % attrs([("name", nm), ("value", "o")])

def form(rng, n):
    parts = ["<form action=\"/go\" method=\"post\">"]
    for _ in range(n):
        c = control(rng)
        if rng.random() < 0.2:
            c = "<div class=\"g\"><label>l</label>%s</div>" % c
        parts.append(c)
        if rng.random() < 0.3:
            parts.append("<p>text</p>")
    parts.append("</form>")
    return "".join(parts)

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        nf, nc = SIZES[size]
        rows = []
        if size == "S":
            rows.append(esc('<form><input name=a value=1><input name=b type=checkbox><input name=c type=checkbox checked><input name=d type=radio checked value=r><input name=e disabled value=x><input value=noname><input name="" value=emptyname><textarea name=t>tt</textarea><select name=s><option value=1>a<option value=2 selected>b<option value=3 selected>c</select><select name=s2><option value=9>z<option>y</select><select name=s3></select><button name=bb value=1>x</button></form>'))
            rows.append(esc("<form></form>"))
        while len(rows) < nf:
            rows.append(esc(form(rng, rng.randint(max(1, nc // 2), nc))))
        write(out, size, rows)

main(sys.argv[1])
