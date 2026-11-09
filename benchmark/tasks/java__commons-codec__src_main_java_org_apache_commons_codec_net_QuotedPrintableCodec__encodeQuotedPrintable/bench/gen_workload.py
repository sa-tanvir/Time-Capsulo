import random, sys, os
SEEDBASE = 20190722
SIZES = {"S": (80, 300), "M": (60, 30000), "L": (30, 600000)}

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, maxlen = SIZES[size]
        lines = []
        for k in range(count):
            if size == "S":
                length = k + 3 if k < 60 else rng.randint(3, maxlen)
            else:
                length = rng.randint(maxlen // 2, maxlen)
            strict = rng.randint(0, 1)
            kind = rng.choice([0, 0, 1, 2])
            if size == "S" and k % 7 == 0:
                strict = 0
                length = rng.randint(0, 2)
            seed = rng.randint(1, 2**31 - 1)
            lines.append("%d %d %d %d" % (strict, kind, length, seed))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

main(sys.argv[1])
