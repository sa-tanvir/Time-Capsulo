import random, sys, os
SEEDBASE = 20190831
# size -> (cases, words per text)
SIZES = {"S": (60, 14), "M": (120, 400), "L": (40, 9000)}
# wrapOn ids (decoded by the driver): 0 null, 1 "", 2 " ", 3 "/", 4 "[ ,;]+", 5 "-", 6 "\\s", 7 " +", 8 "[,.]"
NEWLINE_IDS = 4   # 0 null, 1 "\n", 2 "<br />", 3 "\r\n"
SYL = ["ab", "ra", "ca", "da", "bra", "the", "qu", "ick", "fox", "jum", "ped", "ov", "er", "lazy", "dog", "com", "mons", "text"]
SEPS = [" "] * 14 + ["  ", "   ", ", ", "; ", "/", "-", ". ", " - "]

def word(rng):
    r = rng.random()
    if r < 0.04:
        return "https://www." + "".join(rng.choice(SYL) for _ in range(rng.randint(6, 14))) + ".org/x"
    return "".join(rng.choice(SYL) for _ in range(rng.randint(1, 3)))

def text(rng, nw):
    parts = []
    if rng.random() < 0.15:
        parts.append(" " * rng.randint(1, 3))
    for i in range(nw):
        parts.append(word(rng))
        parts.append(rng.choice(SEPS))
    if rng.random() < 0.5:
        parts.pop()
    return "".join(parts)

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, nw = SIZES[size]
        rows = []
        if size == "S":
            # (wrapLength, newlineId, longWords, wrapOnId, text)
            rows += [(20, 1, 0, 2, "Here is one line of text that is going to be wrapped after 20 columns."),
                     (20, 2, 1, 0, "Here is one line of text that is going to be wrapped after 20 columns."),
                     (20, 0, 0, 1, "Click here to jump to the commons website - https://commons.apache.org"),
                     (20, 1, 1, 2, "Click here to jump to the commons website - https://commons.apache.org"),
                     (7, 1, 0, 2, "word1             word2                        word3"),
                     (0, 1, 0, 2, "Here is one line"), (-5, 1, 1, 2, "Here is one line"), (2, 1, 0, 2, "Here is one line"),
                     (6, 1, 0, 2, "Here is one line"), (20, 1, 0, 2, ""), (20, 1, 1, 2, " Here:  is  one  line  of  text  that  is  going  to  be  wrapped  after  20  columns."),
                     (30, 1, 0, 3, "flammable/inflammable"), (2, 1, 0, 3, "flammable/inflammable"), (9, 1, 1, 3, "flammable/inflammable"),
                     (15, 1, 1, 3, "flammableinflammable"), (2147483647, 1, 0, 2, "aaaa aaaa aaaa"), (3, 1, 1, 4, "ab,, cd;; ef gh"),
                     (4, 3, 0, 6, "ab  cd   ef gh"), (5, 1, 0, 8, "ab,cd.ef,gh.ij,kl")]
        while len(rows) < count:
            wl = rng.choice([5, 10, 20, 40, 72, 80, 120]) if size != "S" else rng.randint(1, 25)
            n = rng.randint(max(1, nw // 2), nw)
            rows.append((wl, rng.randrange(NEWLINE_IDS), rng.randrange(2), rng.choice([0, 1, 2, 2, 2, 3, 4, 5, 6, 7, 8]), text(rng, n)))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join("%d\t%d\t%d\t%d\t%s" % r for r in rows) + "\n")

main(sys.argv[1])
