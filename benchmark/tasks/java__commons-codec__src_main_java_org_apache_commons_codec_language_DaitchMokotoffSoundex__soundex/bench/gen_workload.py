import random, sys, os
TOKENS = ['a', 'e', 'i', 'o', 'u', 'y', 'ai', 'ei', 'ia', 'ch', 'tch', 'sch', 'sh', 'ts', 'tz', 'cz', 'cs', 'zh', 'zs', 'sz', 's', 'z', 'c', 'k', 'h', 'j', 'g', 'b', 'p', 'f', 'v', 'd', 't', 'dt', 'rz', 'rs', 'r', 'l', 'm', 'n', 'mn', 'nm', 'w', 'ow', 'au', 'ue', 'eu', 'oi', 'oy', 'ui', 'ey', 'ij', 'ß', 'ä']
EXTRA = ['', 'Peterson', 'Jackson', 'Moskowitz', 'Moskovitz', 'Auerbach', 'Ohrbach', 'Lipshitz', 'Lippszyc', 'Schwarzenegger', 'Mannheim', 'Zhukov', 'Rosochowaciec', 'Szczepanski', 'Chernyshev', 'Tzvi', 'Tsvi', 'Kleinman', 'Mueller', 'Müller', '  Spaced   Name  ', 'abc-123']
SEEDBASE = 20190722
# size -> (number of strings, token count per string)
SIZES = {"S": (80, 4), "M": (300, 25), "L": (200, 250)}
HEADER = {"S": [], "M": [], "L": []}

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
