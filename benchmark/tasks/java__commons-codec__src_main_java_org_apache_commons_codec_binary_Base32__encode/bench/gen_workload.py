import random, sys, os
SEEDBASE = 20190722
# size -> (cases, max length)
SIZES = {"S": (60, 70), "M": (60, 6000), "L": (30, 400000)}

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, maxlen = SIZES[size]
        lines = []
        for k in range(count):
            if size == "S":
                length = k if k < 40 else rng.randint(0, maxlen)
            else:
                length = rng.randint(maxlen // 2, maxlen)
            line_length = rng.choice([0, 0, 76, 64, 10, 20, 1])
            variant = rng.randint(0, 1)
            sep = rng.randint(0, 1)
            chunk = rng.choice([0, 0, 1, 3, 5, 7, 16, 100, 4096])
            seed = rng.randint(1, 2**31 - 1)
            lines.append("%d %d %d %d %d %d" % (line_length, variant, sep, chunk, length, seed))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

main(sys.argv[1])
