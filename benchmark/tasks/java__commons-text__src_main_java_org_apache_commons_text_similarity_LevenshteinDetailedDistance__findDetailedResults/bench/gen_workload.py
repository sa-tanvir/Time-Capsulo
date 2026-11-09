import random, sys, os
SEEDBASE = 20190831
# size -> (pairs, base length, inner repetition is in the driver)
SIZES = {"S": (60, 12), "M": (60, 120), "L": (40, 700)}
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
        pairs = []
        if size == "S":
            pairs += [("kitten", "sitting"), ("a", "b"), ("a", "a"), ("abc", "abc"), ("a", "abc"), ("abc", "a"),
                      ("flaw", "lawn"), ("hello", "hallo"), ("ab", "ba"), ("abc", "xyz"), ("aaa", "a"), ("a", "aaa"),
                      ("ten", "n"), ("elephant", "hippo"), ("hippo", "elephant")]
        while len(pairs) < count:
            n = rng.randint(max(1, ln // 2), ln)
            a = "".join(rng.choice(ALPHA) for _ in range(n))
            r = rng.random()
            if r < 0.7:
                b = mutate(rng, a, rng.choice([0.05, 0.2, 0.5]))
            else:
                b = "".join(rng.choice(ALPHA) for _ in range(rng.randint(max(1, ln // 2), ln)))
            if not b:
                b = "a"
            pairs.append((a, b))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write("\n".join(a + "\t" + b for a, b in pairs) + "\n")

main(sys.argv[1])
