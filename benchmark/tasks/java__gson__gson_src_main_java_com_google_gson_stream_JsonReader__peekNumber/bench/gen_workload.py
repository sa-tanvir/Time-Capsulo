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

SIZES = {"S": (500, 12), "M": (4000, 120), "L": (30000, 1000)}
FIXED = ["0", "-0", "00", "01", "-01", "1", "-1", "12", "-12", "1.5", "-1.5", "0.5", "-0.5", "0.0", "-0.0", "1e5", "1E5", "1e+5", "1E-5", "-1e5",
         "1.5e10", "1.5E-10", "0e0", "0e1", "-0e1", "-", "+1", "1.", ".5", "-.5", "1e", "1e+", "1e-", "1.e5", "1e5.5", "1e5e5", "1-", "1+", "-1-", "--1",
         "1.5.5", "1x", "12a", "12abc", "1 ", "12 ", "12,", "12]", "12}", "12:", "12\n", "12\t", "12\r", "12\f", "12/", "12#", "12;", "12=", "12\\", "12/*",
         "9223372036854775807", "9223372036854775806", "-9223372036854775808", "-9223372036854775807", "9223372036854775808", "-9223372036854775809",
         "922337203685477580", "9223372036854775800", "9223372036854775810", "92233720368547758070", "-922337203685477580", "-922337203685477581",
         "1234567890123456789", "12345678901234567890", "0.", "0.0e", "-", "", "true", "null", "e5", "E", "1ee5", "12e", "1.5e+", "5e+5", "5E-5", "123456789012345678901234567890",
         "1,2", "[1]", "{1}", "1\"", "1'", "1_000", "٣", "1é"]
def gen(rng, size):
    nc, ln = SIZES[size]
    rows = []
    if size == "S":
        for t in FIXED:
            for chunk, lenient in ((0, False), (rng.choice(CHUNKS), True)):
                rows.append(row(chunk, lenient, 1, t, "", 0, ""))
    def num(k):
        r = rng.random()
        pre = rng.choice(["", "", "-"])
        unit = "".join(rng.choice("0123456789") for _ in range(rng.choice([1, 2, 3, 5, 10])))
        if unit[0] == "0" and rng.random() < 0.9: unit = "7" + unit[1:]
        cnt = max(1, k // len(unit))
        if r < 0.45: suf = ""
        elif r < 0.6: suf = "." + "".join(rng.choice("0123456789") for _ in range(rng.randint(1, 9)))
        elif r < 0.7: suf = "e" + rng.choice(["", "+", "-"]) + str(rng.randint(1, 99))
        elif r < 0.8: suf = rng.choice(["", ".5"]) + "E" + str(rng.randint(1, 300))
        else: suf = rng.choice(["x", "-", ".", "e", "..", "+", "0x", "e+"])
        term = rng.choice(["", " ", ",", "]", "}", "\n", "/", "#", "q", "\t", ":"])
        return pre, unit, cnt, suf + term
    while len(rows) < nc:
        k = rng.randint(max(1, ln // 4), ln)
        pre, unit, cnt, suf = num(k)
        if size == "L" and rng.random() < 0.08:
            pre, unit, cnt, suf = "-", "9", rng.randint(1015, 1030), ""  # around the 1024-char buffer limit
        lenient = rng.random() < 0.5
        rows.append(row(rng.choice(CHUNKS), lenient, 1, pre, unit, cnt, suf))
    return rows


def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        write(out, size, gen(rng, size))

main(sys.argv[1])
