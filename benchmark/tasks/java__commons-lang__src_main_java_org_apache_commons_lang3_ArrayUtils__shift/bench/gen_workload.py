import random, sys, os
SEEDBASE = 20190411
# size -> (cases, array length)
SIZES = {"S": (80, 12), "M": (80, 3000), "L": (24, 6000000)}

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, ln = SIZES[size]
        rows = []  # len, start, end, offset, seed
        if size == "S":
            rows += [(-1, 1, 1, 1, 1), (0, 0, 0, 1, 1), (1, 0, 1, 1, 1), (2, 0, 2, 1, 2), (5, 1, 3, 1, 3), (5, 1, 4, 2, 3), (4, 1, 1, 1, 4), (4, 0, 4, 4, 5),
                     (4, 0, 4, -4, 5), (4, 0, 4, 1, 5), (4, 0, 4, -1, 5), (6, 0, 6, 3, 6), (6, 0, 6, 2, 6), (6, 0, 6, 4, 6), (6, -3, 100, 2, 7), (6, 3, 2, 1, 7),
                     (6, 5, 6, 1, 7), (6, 4, 6, 1, 7), (6, 0, 0, 1, 7), (6, 0, -2, 1, 7), (6, 2, 5, -7, 8), (6, 2, 5, 2147483647, 8), (6, 0, 6, -2147483648, 8)]
        while len(rows) < count:
            n = rng.randint(max(2, ln // 2), ln)
            r = rng.random()
            if r < 0.4:
                s, e = 0, n
            elif r < 0.9:
                s = rng.randint(0, n // 3)
                e = rng.randint(n - n // 3, n)
            else:
                s = rng.randint(-5, n + 3)
                e = rng.randint(-5, n + 5)
            o = rng.choice([rng.randint(-3 * n, 3 * n), rng.randint(1, 5), -rng.randint(1, 5), n // 2, n // 2 + 1, n - 1, rng.randint(-2**31, 2**31 - 1)])
            rows.append((n, s, e, o, rng.randint(0, 10**6)))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write("\n".join("\t".join(str(v) for v in r) for r in rows) + "\n")

main(sys.argv[1])
