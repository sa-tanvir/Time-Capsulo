import random, sys, os
SEEDBASE = 20190411
# size -> (cases, max bit length of the operands)
SIZES = {"S": (150, 12), "M": (20000, 22), "L": (300000, 31)}
MIN, MAX = -2**31, 2**31 - 1

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, bits = SIZES[size]
        rows = []
        if size == "S":
            specials = [0, 1, -1, 2, -2, 3, 6, -6, 7, 12, -18, 100, 1024, MAX, MIN, MIN + 1, 2**30, -2**30, 46341, 65536]
            for a in specials:
                for b in specials[:12] + [MAX, MIN, 2**30]:
                    rows.append((a, b))
        while len(rows) < count:
            kind = rng.random()
            if kind < 0.5:      # unrelated operands
                a = rng.randint(-(2**bits) + 1, 2**bits - 1)
                b = rng.randint(-(2**bits) + 1, 2**bits - 1)
            elif kind < 0.9:    # common factor
                g = rng.randint(1, 2**(bits // 2))
                a = g * rng.randint(-(2**(bits // 2)), 2**(bits // 2))
                b = g * rng.randint(-(2**(bits // 2)), 2**(bits // 2))
            else:               # powers of two mixed in
                s = rng.randint(0, bits - 1)
                a = rng.randint(-(2**(bits - s)) + 1, 2**(bits - s) - 1) << s
                b = rng.randint(-(2**(bits - s)) + 1, 2**(bits - s) - 1) << rng.randint(0, s)
            a = max(MIN, min(MAX, a))
            b = max(MIN, min(MAX, b))
            rows.append((a, b))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write("\n".join("%d\t%d" % r for r in rows[:max(count, len(rows))]) + "\n")

main(sys.argv[1])
