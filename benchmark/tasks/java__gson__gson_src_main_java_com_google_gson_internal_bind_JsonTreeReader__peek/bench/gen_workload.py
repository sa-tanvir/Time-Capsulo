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

SIZES = {"S": (120, 30, 3, 4), "M": (200, 500, 8, 6), "L": (60, 20000, 40, 8)}
EXPL = ["{}", "[]", "null", "\"s\"", "1", "1.5", "true", "[[],{}]", "[{},[]]", "{\"a\":[1,{\"b\":null}],\"c\":{}}", "[1,2,[3,[4,[]]]]",
        "{\"a\":{\"b\":{\"c\":{}}}}", "[null,true,\"x\",2,[ ]]", "{\"a\":1,\"b\":2,\"c\":3}", "[[[[[[[[1]]]]]]]]", "[{\"x\":[]},{\"y\":{}}]"]
def gen(rng, size):
    nc, nodes, depth, fan = SIZES[size]
    rows = []
    if size == "S":
        for t in EXPL:
            for v in "FPSMDC":
                rows.append("\t".join(["X", v, esc(t)]))
    while len(rows) < nc:
        v = rng.choice("FFPSMD")
        nn = rng.randint(max(1, nodes // 2), nodes)
        rows.append("\t".join(["G", v, str(rng.randint(1, 10**9)), str(nn), str(rng.randint(1, depth)), str(rng.randint(1, fan))]))
    return rows


def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        write(out, size, gen(rng, size))

main(sys.argv[1])
