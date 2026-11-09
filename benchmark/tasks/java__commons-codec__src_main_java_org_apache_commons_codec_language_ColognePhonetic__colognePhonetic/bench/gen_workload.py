import random, sys, os
TOKENS = ['a', 'e', 'i', 'o', 'u', 'y', 'j', 'ä', 'ö', 'ü', 'ß', 'b', 'p', 'ph', 'd', 't', 'dt', 'f', 'v', 'w', 'g', 'k', 'q', 'ck', 'x', 's', 'z', 'c', 'ca', 'ch', 'cs', 'sch', 'h', 'r', 'l', 'm', 'n', 'mann', 'berg', 'stein', 'sz', 'tz', '-', "'", ' ']
EXTRA = ['', 'Müller-Lüdenscheidt', 'Wikipedia', 'Breschnew', 'Meyer', 'Meier', 'Maier', 'Mayr', 'Schmidt', 'Schmitt', 'Xaver', 'Christoph', 'Christian', 'Zimmermann', 'Äpfel Öl Über', 'Straße', '42', 'abc123', '  ', 'Phönix']
SEEDBASE = 20190722
# size -> (number of strings, token count per string)
SIZES = {"S": (80, 4), "M": (300, 40), "L": (800, 400)}
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
