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

NCHAIN = 40
SIZES = {"S": (4, 0), "M": (12, 1500), "L": (40, 1200)}   # chain depth, random chain cases
PARAM = ["List<String>", "List<Number>", "List<Integer>", "List<?>", "List<? extends Number>", "Collection<String>", "Iterable<String>", "Map<String,Integer>", "Map<String,String>",
         "Map<String,List<String>>", "Set<String>", "Set<List<String>>", "Comparable<String>", "ArrayList<String>", "ArrayList<Integer>", "HashMap<String,Integer>", "LinkedList<String>",
         "A<String>", "A<Integer>", "B<String>", "B<Integer>", "I0<String>", "I1<String>", "I1<Integer>", "I0<List<String>>", "E2<String,String>", "A<List<String>>", "A<List<Integer>>", "A<T>", "A<U>"]
RAW = ["C", "ArrayList", "String", "Object", "Integer", "A", "B", "List", "int[]", "List<String>[]", "TV:T", "WC:Number", "null"]
def gen(rng, size):
    depth, nrand = SIZES[size]
    rows = []
    if size == "S":
        for f in PARAM + RAW:
            for t in PARAM:
                rows.append("\t".join([f, t, ""]))
        for f in ["A<T>", "A<U>", "B<String>", "C"]:
            for t in ["A<String>", "A<Integer>", "I0<String>", "A<List<String>>"]:
                rows.append("\t".join([f, t, "T=String"]))
                rows.append("\t".join([f, t, "T=Integer,U=String"]))
    argz = ["String", "Integer", "Number"]
    while len(rows) < len(rows) + 0 and False: pass
    n0 = len(rows)
    for i in range(nrand if size != "S" else 120):
        d = rng.randint(max(1, depth // 2), depth)
        src = NCHAIN - d
        kind = rng.random()
        fa = rng.choice(argz[:2])
        frm = "D%d:%s" % (src, fa)
        if kind < 0.35:
            to = "J%d:%s" % (rng.randint(0, NCHAIN), rng.choice([fa, fa, "Number"]))
        elif kind < 0.7:
            y = rng.randint(src, NCHAIN) if rng.random() < 0.75 else rng.randint(0, NCHAIN)
            to = "D%d:%s" % (y, rng.choice([fa, fa, fa, "Number"]))
        elif kind < 0.85:
            frm = rng.choice(PARAM + RAW); to = rng.choice(PARAM)
        else:
            to = "J%d:%s" % (rng.randint(0, NCHAIN), fa)
        rows.append("\t".join([frm, to, ""]))
    return rows


def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        write(out, size, gen(rng, size))

main(sys.argv[1])
