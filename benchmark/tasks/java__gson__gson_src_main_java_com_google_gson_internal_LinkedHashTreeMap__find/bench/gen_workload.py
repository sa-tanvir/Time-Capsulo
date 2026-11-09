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

SEED = 20191005 + 0
CHUNKS = [0, 0, 0, 1, 2, 3, 5, 7, 64, 1000]

def row(chunk, lenient, calls, pre, unit, count, suf):
    # fields: chunk, flag(L=lenient,S=strict), calls, prefix, unit, count, suffix (text = prefix + unit*count + suffix)
    return "\t".join([str(chunk), "L" if lenient else "S", str(calls), esc(pre), esc(unit), str(count), esc(suf)])

HASH = True
MODE = 'find'

SIZES = {"S": (60, 20, 30), "M": (100, 300, 200), "L": (150, 6000, 3000)}  # cases, ops per case, keyspace
def gen(rng, size):
    nc, nops, ks = SIZES[size]
    rows = []
    HM = [1, 3, 16, 1000000] if HASH else [1000000]
    def explicit(cmp, hm, ks_, ops):
        rows.append("\t".join(["E", cmp, str(hm), str(ks_), ",".join(ops)]))
    if size == "S":
        for hm in HM:
            for cmp in "NR":
                if cmp == "N":
                    explicit(cmp, hm, 16, ["x0", "y0", "p1", "x0", "y0", "g1", "x0", "y0"])
                    explicit(cmp, hm, 16, ["p0", "x0", "y0", "r0", "x0", "y0"])
                explicit(cmp, hm, 16, ["p%d" % i for i in range(10)] + ["g3", "f4", "n11", "n5", "c9", "c12"])
                explicit(cmp, hm, 16, ["p%d" % i for i in range(9, -1, -1)] + ["r0", "r5", "r9", "r7", "r3", "r3"])
                explicit(cmp, hm, 16, ["p%d" % i for i in (5, 2, 8, 1, 3, 7, 9, 0, 4, 6)] + ["r%d" % i for i in (5, 2, 8)])
                explicit(cmp, hm, 16, ["p2", "p0", "p1", "p4", "p6", "p5", "p3", "r2", "r4", "r0", "r6", "r1"])
                explicit(cmp, hm, 16, ["p0", "p1", "p2", "r0", "r1", "r2", "p0", "p0", "n0", "n1", "f1"])
    while len(rows) < nc:
        i = len(rows)
        if MODE == "find":
            pat = rng.choice(["R", "R", "R", "A", "D", "Z"])
            put, rem = rng.choice([(30, 0), (40, 5), (50, 10), (25, 15), (60, 0)])
        else:
            pat = rng.choice(["R", "A", "D", "Z", "Z"])
            put, rem = rng.choice([(100, 0), (70, 25), (50, 45), (60, 30), (85, 10), (80, 20)])
        hm = rng.choice(HM)
        cmp = rng.choice("NNR")
        rows.append("\t".join(["G", cmp, str(hm), str(ks), str(nops), str(rng.randint(1, 10**9)), str(put), str(rem), pat]))
    return rows


def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        write(out, size, gen(rng, size))

main(sys.argv[1])
