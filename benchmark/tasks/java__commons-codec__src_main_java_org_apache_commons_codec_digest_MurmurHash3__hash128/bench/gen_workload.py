import random, sys, os
SEEDBASE = 20190722
SIZES = {"S": (80, 70), "M": (60, 20000), "L": (40, 1000000)}

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, maxlen = SIZES[size]
        lines = []
        for k in range(count):
            if size == "S":
                length = k if k < 50 else rng.randint(0, maxlen)
            else:
                length = rng.randint(maxlen // 2, maxlen)
            offset = rng.choice([0, 0, 1, 3, 7, 16])
            seed = rng.choice([0, 1, -1, 104729, 2**31 - 1, -2**31, rng.randint(-2**31, 2**31 - 1)])
            dseed = rng.randint(1, 2**31 - 1)
            lines.append("%d %d %d %d" % (length, offset, seed, dseed))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

main(sys.argv[1])
