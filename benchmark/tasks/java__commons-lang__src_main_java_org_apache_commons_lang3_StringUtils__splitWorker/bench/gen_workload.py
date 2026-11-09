import random, sys, os
SEEDBASE = 20190411
# size -> (cases, words per text, repetitions)
SIZES = {"S": (70, 8, 1), "M": (70, 400, 3), "L": (20, 1500, 220)}

def esc(s):
    if s is None:
        return "<null>"
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, words, reps = SIZES[size]
        rows = []  # str, rep, sep, max, preserve
        if size == "S":
            rows += [
                (None, 1, " ", 0, 0), (None, 1, None, 0, 1), ("", 1, " ", 0, 0), ("", 1, None, 5, 1), ("abc", 1, "", 0, 0),
                ("abc", 1, "", 0, 1), ("a b  c", 1, None, 0, 0), ("a b  c", 1, None, 0, 1), ("a b  c", 1, " ", 0, 1), (" a ", 1, " ", 0, 1),
                (" a ", 1, " ", 0, 0), ("   ", 1, " ", 0, 1), ("   ", 1, " ", 0, 0), ("a:b:c", 1, ":", 2, 0), ("a:b:c", 1, ":", 1, 0),
                ("a:b:c:", 1, ":", 2, 1), ("a:b:c:", 1, ":", 3, 1), ("a:b:c:", 1, ":", 4, 1), ("a:b:c:", 1, ":", 4, 0), ("a b  c d", 1, " ", 3, 0),
                ("a b  c d", 1, " ", 3, 1), ("a b ", 1, " ", 2, 0), ("a b ", 1, " ", 2, 1), (" a b ", 1, None, 1, 0), (" a b ", 1, None, 1, 1),
                ("a,b;c d", 1, ",; ", 0, 0), ("a,,b;;c", 1, ",;", 0, 1), ("a,,b;;c", 1, ",;", 2, 1), ("a,,b;;c", 1, ",;", 3, 0),
                ("a\tb\nc\r\nd", 1, None, 0, 0), ("a\tb\nc\r\nd", 1, None, 0, 1), ("abc", 1, "x", 5, 1), ("abc", 1, "c", 0, 1), ("abc", 1, "c", 0, 0),
                ("abc", 1, "a", 0, 1), ("abc", 1, "a", 2, 1), ("abc", 1, "b", 1, 1), ("ab", 1, "ab", 0, 1), ("ab", 1, "ab", 0, 0),
            ]
        seps = [None, " ", ",", ";", ", ", ",;:", "|", "\\"]
        while len(rows) < count:
            sep = rng.choice(seps)
            chars = (sep if sep else " \t\n")
            ws = []
            for _ in range(words):
                r = rng.random()
                if r < 0.1:
                    ws.append("")
                else:
                    ws.append("".join(rng.choice("abcdefghijklmnop") for _ in range(rng.randint(1, 9))))
            text = ""
            for w in ws:
                text += w + rng.choice(chars) * (1 if rng.random() < 0.7 else rng.randint(2, 3))
            if rng.random() < 0.3:
                text = rng.choice(chars) + text
            if rng.random() < 0.5:
                text = text.rstrip(chars)
            mx = rng.choice([0, 0, 0, 1, 2, 5, 40, 3000, -1])
            rows.append((text, reps, sep, mx, rng.randint(0, 1)))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            for t, rp, s, mx, pr in rows:
                f.write("\t".join([esc(t), str(rp), esc(s), str(mx), str(pr)]) + "\n")

main(sys.argv[1])
