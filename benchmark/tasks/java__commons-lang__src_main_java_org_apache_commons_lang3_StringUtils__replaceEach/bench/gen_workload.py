import random, sys, os
SEEDBASE = 20190411
# size -> (cases, words per text, repetitions of the text, number of search strings)
SIZES = {"S": (60, 12, 1, 4), "M": (60, 300, 4, 8), "L": (24, 400, 160, 14)}
VOCAB = ["".join(random.Random(i).choice("abcdefgh") for _ in range(random.Random(i).randint(2, 5))) for i in range(60)]

def esc(s):
    if s is None:
        return "<null>"
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")

def arr(a):
    if a is None:
        return "<null>"
    if not a:
        return "A"
    return "A" + "\x1f".join("N" if x is None else "E" + esc(x) for x in a)

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, words, reps, k = SIZES[size]
        rows = []  # text, rep, search, repl, repeat, ttl
        if size == "S":
            E = [
                (None, 1, ["a"], ["b"], 0, 0), ("", 1, ["a"], ["b"], 0, 0), ("aba", 1, None, None, 0, 0),
                ("aba", 1, [], None, 0, 0), ("aba", 1, None, [], 0, 0), ("aba", 1, ["a"], None, 0, 0),
                ("aba", 1, ["a"], [""], 0, 0), ("aba", 1, [None], ["a"], 0, 0), ("aba", 1, ["a"], [None], 0, 0),
                ("aba", 1, ["a", "b"], ["c", None], 0, 0), ("aba", 1, ["", "a"], ["x", "y"], 0, 0),
                ("abcde", 1, ["ab", "d"], ["w", "t"], 0, 0), ("abcde", 1, ["ab", "d"], ["d", "t"], 0, 0),
                ("abc", 1, ["a", "b"], ["b", "c"], 0, 0), ("abc", 1, ["a", "b"], ["b", "c"], 1, 2),
                ("abcde", 1, ["ab", "d"], ["d", "t"], 1, 2), ("abba", 1, ["a"], ["b", "a"], 0, 0),
                ("abcde", 1, ["ab", "d"], ["d", "ab"], 1, 2), ("abcde", 1, ["ab", "d"], ["d", "ab"], 1, -1),
                ("abc", 1, ["a"], ["b"], 0, -1), ("", 1, ["a"], ["b"], 1, -1), (None, 1, None, None, 0, -1),
                ("aaaa", 1, ["a"], ["aa"], 1, 3), ("aaaa", 1, ["aa", "a"], ["b", "c"], 0, 0), ("aaaa", 1, ["a", "aa"], ["b", "c"], 0, 0),
                ("dcba", 1, ["a", "b", "c", "d"], ["b", "c", "d", "e"], 1, 4), ("dcba", 1, ["a", "b", "c", "d"], ["b", "c", "d", "e"], 1, 3),
                ("dcba", 1, ["a", "b", "c", "d"], ["b", "c", "d", "e"], 1, 0), ("xyz", 1, ["q"], ["r"], 1, 1),
                ("the quick brown fox", 1, ["quick", "fox", "the"], ["slow", "dog", "a"], 0, 0),
                ("ab", 1, ["abc"], ["x"], 0, 0), ("ab", 1, ["ab"], [""], 1, 1),
            ]
            rows += E
        while len(rows) < count:
            text = " ".join(rng.choice(VOCAB) for _ in range(words))
            srch = rng.sample(VOCAB, k)
            kind = rng.random()
            if kind < 0.35:      # plain replacements from a disjoint alphabet
                repl = ["".join(rng.choice("XYZW") for _ in range(rng.randint(0, 7))) for _ in srch]
                repeat, ttl = 0, 0
            elif kind < 0.6:
                repl = ["".join(rng.choice("XYZW") for _ in range(rng.randint(0, 7))) for _ in srch]
                repeat, ttl = 1, len(srch)
            elif kind < 0.8:     # chained replacements, multiple passes
                repl = srch[1:] + ["QQ"]
                repeat, ttl = 1, len(srch)
            else:                # with some null entries and prefix-overlapping search strings
                repl = ["".join(rng.choice("XYZW") for _ in range(rng.randint(1, 4))) for _ in srch]
                for j in range(len(repl)):
                    if rng.random() < 0.2:
                        repl[j] = None
                    if rng.random() < 0.1:
                        srch[j] = None
                    elif rng.random() < 0.15:
                        srch[j] = srch[j][:1]
                repeat, ttl = 0, 0
            rows.append((text, reps, srch, repl, repeat, ttl))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            for t, rp, s, r, rpt, ttl in rows:
                f.write("\t".join([esc(t), str(rp), arr(s), arr(r), str(rpt), str(ttl)]) + "\n")

main(sys.argv[1])
