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
# size -> (haystack length, groups, queries per group)
SIZES = {"S": (50, 6, 12), "M": (3000, 4, 100), "L": (24000, 3, 700)}

def main(out):
    for i, size in enumerate("SML"):
        rng = random.Random(SEED + i)
        hl, ng, nq = SIZES[size]
        rows = []
        for g in range(ng):
            alpha = "abc" if g % 2 == 0 else "abcdefgh"
            hay = "".join(rng.choice(alpha) for _ in range(hl))
            if g == 0: hay = "aaab" * (hl // 4) + "c" * (hl - 4 * (hl // 4))
            rows.append("H\t" + esc(hay))
            pos = 0
            for _ in range(nq):
                d = rng.randint(0, max(1, hl // nq) * 2)
                if pos + d >= hl - 1: d = 0
                pos += d
                r = rng.random()
                ln = rng.choice([1, 1, 2, 3, 4, 6, 9, 14])
                if r < 0.45 and pos < hl:
                    p = rng.randint(pos, hl - 1)
                    seq = hay[p:p + ln]
                elif r < 0.7:
                    seq = "".join(rng.choice(alpha) for _ in range(ln + 3))
                elif r < 0.8:
                    seq = "aab"[: rng.randint(1, 3)] + "z"
                elif r < 0.9:
                    seq = hay[pos: pos + ln + 40]
                else:
                    seq = "".join(rng.choice(alpha) for _ in range(ln))
                rows.append("Q\t%d\t%s" % (d, esc(seq)))
        if size == "S":
            rows += ["H\tabcabcabc", "Q\t0\tabc", "Q\t1\tabc", "Q\t2\tcab", "Q\t0\tabcabcabcd", "Q\t3\tc", "Q\t0\tz", "Q\t0\tabcabcabc"]
        write(out, size, rows)

main(sys.argv[1])
