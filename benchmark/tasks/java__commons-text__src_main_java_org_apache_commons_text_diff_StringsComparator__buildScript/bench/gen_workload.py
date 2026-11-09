import random, sys, os
SEEDBASE = 20190901
SIZES = {"S": (40, 14), "M": (40, 300), "L": (25, 3000)}
ALPHA = "abcdefghij"

def mutate(rng, s, rate):
    out = []
    for ch in s:
        r = rng.random()
        if r < rate / 2:
            continue
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
            for a, b in [("abcabba", "cbabac"), ("kitten", "sitting"), ("abc", "abc"), ("abc", "xyz"), ("a", "b"),
                         ("a", "abc"), ("abc", "a"), ("", "abc"), ("abc", ""), ("ab", "ba"), ("abcdef", "abcdef"),
                         ("aaaa", "aa"), ("xaxbxc", "abc")]:
                rows.append((a, b, 0, len(a), 0, len(b)))
        while len(rows) < count:
            n = rng.randint(max(1, ln // 2), ln)
            a = "".join(rng.choice(ALPHA) for _ in range(n))
            if rng.random() < 0.8:
                b = mutate(rng, a, rng.choice([0.01, 0.05, 0.1]))
            else:
                b = "".join(rng.choice(ALPHA) for _ in range(rng.randint(max(1, ln // 2), ln)))
            rows.append((a, b, 0, len(a), 0, len(b)))
            if False:
                s1 = rng.randint(0, len(a) // 2); e1 = rng.randint(s1, len(a))
                s2 = rng.randint(0, len(b) // 2); e2 = rng.randint(s2, len(b))
                rows.append((a, b, s1, e1, s2, e2))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write("\n".join("\t".join(map(str, r)) for r in rows) + "\n")

main(sys.argv[1])
