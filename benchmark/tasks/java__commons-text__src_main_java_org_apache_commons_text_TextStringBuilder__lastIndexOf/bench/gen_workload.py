import random, sys, os
SEEDBASE = 20190831
# size -> (haystack length, queries)
SIZES = {"S": (60, 80), "M": (6000, 200), "L": (400000, 300)}
ALPHA = "abcd"

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        hl, nq = SIZES[size]
        hay = "".join(rng.choice(ALPHA) for _ in range(hl))
        rows = []
        if size == "S":
            rows += [(0, ""), (5, ""), (-1, "a"), (-3, ""), (1000, ""), (1000, "a"), (hl - 1, hay), (hl - 1, hay + "a"), (hl - 2, hay),
                     (hl, hay[-3:]), (0, hay[:1]), (0, hay[:2]), (3, hay[:4]), (5, "<null>"), (1000, "qq"), (hl - 1, "qqq"), (hl + 5, hay[-5:] + "q")]
        while len(rows) < nq:
            r = rng.random()
            ln = rng.choice([1, 2, 3, 5, 8, 12]) if size != "S" else rng.randint(1, 5)
            if r < 0.5:
                p = rng.randrange(0, max(1, hl - ln))
                needle = hay[p:p + ln]
            elif r < 0.7:
                needle = "".join(rng.choice(ALPHA) for _ in range(ln + 6))
            elif r < 0.8:
                needle = "".join(rng.choice("abcdq") for _ in range(ln))
            elif r < 0.85:
                needle = ""
            else:
                needle = "".join(rng.choice(ALPHA) for _ in range(ln))
            c = rng.random()
            if c < 0.6:
                start = rng.randint(0, hl - 1)
            elif c < 0.8:
                start = hl + rng.randint(0, 10)
            else:
                start = -rng.randint(0, 3)
            rows.append((start, needle))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write(hay + "\n" + "\n".join("%d\t%s" % r for r in rows) + "\n")

main(sys.argv[1])
