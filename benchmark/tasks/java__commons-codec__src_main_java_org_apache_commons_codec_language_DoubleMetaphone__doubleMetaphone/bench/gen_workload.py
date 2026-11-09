import random, sys, os
TOKENS = ['ch', 'sch', 'gh', 'ph', 'th', 'sh', 'c', 'ci', 'ce', 'cc', 'g', 'gn', 'j', 'k', 'kn', 'l', 'll', 'm', 'mb', 'n', 'p', 'pn', 'q', 'r', 's', 'sc', 't', 'tion', 'w', 'wr', 'x', 'z', 'zz', 'a', 'e', 'i', 'o', 'u', 'y', 'b', 'd', 'dg', 'f', 'h', 'v', 'Ç', 'Ñ', 'bacher', 'caesar', 'mc', 'ough', 'gia', 'igh']
EXTRA = ['', 'Smith', 'Schmidt', 'Caesar', 'Michael', 'Thompson', 'Gnome', 'Xavier', 'Wright', 'Knight', 'Josef', 'Jose', 'Mac Hugh', 'Bacher', 'MaÇon', 'SeÑor', 'Czerny', 'Dumb', 'Thumb', 'Hugh', 'Aubrey', 'Bough', 'Laugh', 'Cough', 'Ghislane', 'Yankelovich', 'Zhao', 'Island', 'Edge', 'Dodgy', '  padded  ', 'abc123!?', '123']
SEEDBASE = 20190722
# size -> (number of strings, token count per string)
SIZES = {"S": (80, 3), "M": (300, 40), "L": (700, 400)}
HEADER = {"S": ["8"], "M": ["64"], "L": ["1000"]}

def word(rng, ntok):
    return "".join(rng.choice(TOKENS) for _ in range(ntok))

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, ntok = SIZES[size]
        lines = list(HEADER[size])
        if size == "S":
            lines += EXTRA
        for _ in range(count):
            n = rng.randint(max(1, ntok // 2), ntok)
            w = word(rng, n)
            r = rng.random()
            if r < 0.15:
                w = w.upper()
            elif r < 0.25:
                w = w.capitalize()
            elif r < 0.3:
                w = " " + w + " "
            lines.append(w)
        with open(os.path.join(out, "workload_%s.txt" % size), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

main(sys.argv[1])
