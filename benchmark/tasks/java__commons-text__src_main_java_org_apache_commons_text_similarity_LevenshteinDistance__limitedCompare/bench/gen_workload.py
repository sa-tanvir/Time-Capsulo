import random, sys, os
SEEDBASE = 20190831
SIZES = {"S": (80, 12), "M": (80, 150), "L": (60, 2500)}
ALPHA = "abcdefgh"

def mutate(rng, s, rate):
    out = []
    for ch in s:
        r = rng.random()
        if r < rate / 3:
            continue
        elif r < 2 * rate / 3:
            out.append(rng.choice(ALPHA))
        elif r < rate:
            out.append(ch)
            out.append(rng.choice(ALPHA))
        else:
            out.append(ch)
    return "".join(out)

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, ln = SIZES[size]
        rows = []
        if size == "S":
            rows += [("kitten", "sitting", 3), ("kitten", "sitting", 2), ("kitten", "sitting", 0), ("", "", 0), ("", "abc", 3),
                     ("", "abc", 2), ("abc", "", 3), ("abc", "", 1), ("abc", "abc", 0), ("a", "b", 0), ("a", "b", 1),
                     ("abcdefg", "a", 3), ("a", "abcdefg", 6), ("a", "abcdefg", 7), ("hello", "hallo", 1),
                     ("<null>", "x", 1), ("x", "<null>", 1), ("ab", "ba", 1), ("ab", "ba", 2), ("elephant", "hippo", 7), ("elephant", "hippo", 8),
                     ("abc", "abd", -1)]
        while len(rows) < count:
            n = rng.randint(max(1, ln // 2), ln)
            a = "".join(rng.choice(ALPHA) for _ in range(n))
            if rng.random() < 0.75:
                b = mutate(rng, a, rng.choice([0.02, 0.1, 0.3]))
            else:
                b = "".join(rng.choice(ALPHA) for _ in range(rng.randint(max(1, ln // 2), ln)))
            r = rng.random()
            if r < 0.15:
                t = rng.randint(0, 3)
            elif r < 0.5:
                t = max(0, int(ln * rng.choice([0.05, 0.15, 0.3])))
            elif r < 0.8:
                t = abs(len(a) - len(b)) + rng.randint(0, max(1, ln // 4))
            else:
                t = 3 * ln
            rows.append((a, b, t))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write("\n".join("%s\t%s\t%d" % r for r in rows) + "\n")

main(sys.argv[1])
