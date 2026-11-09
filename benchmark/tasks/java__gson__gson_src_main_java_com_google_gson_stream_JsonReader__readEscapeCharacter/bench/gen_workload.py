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

SIZES = {"S": (400, 3), "M": (4000, 30), "L": (6000, 300)}
VALID = ["n", "t", "r", "b", "f", "\"", "'", "\\", "/", "u0041", "u00e9", "u20AC", "uD83D", "ude00", "u0000", "uabcd", "uFFFF", "u0019", "\n"]
BAD = ["q", "x", "0", "a", " ", "u000g", "uZZZZ", "u12", "u", "u123", "", "u-123", "U0041", "\r"]
def gen(rng, size):
    nc, rep = SIZES[size]
    rows = []
    if size == "S":
        for b in VALID + BAD:
            for chunk in (0, 1, 2, 5):
                rows.append(row(chunk, False, 1, b, "", 0, ""))
                rows.append(row(chunk, True, 1, b, "", 0, "tail"))
        for b in BAD:
            rows.append(row(0, False, 2, "n", b, 1, ""))
    while len(rows) < nc:
        k = rng.randint(2, 8)
        unit = "".join(rng.choice(VALID) for _ in range(k))
        unit_calls = unit.count("u") * 0  # computed below
        # count escapes in unit: each element of VALID is one escape
        seq = [rng.choice(VALID) for _ in range(k)]
        unit = "".join(seq)
        cnt = max(1, rng.randint(max(1, rep // 2), rep))
        total_calls = cnt * k
        suf = ""
        calls = total_calls
        r = rng.random()
        if r < 0.08 and size != "L":
            suf = rng.choice(BAD); calls = total_calls + 1
        rows.append(row(rng.choice(CHUNKS), False, calls, "", unit, cnt, suf))
    return rows


def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        write(out, size, gen(rng, size))

main(sys.argv[1])
