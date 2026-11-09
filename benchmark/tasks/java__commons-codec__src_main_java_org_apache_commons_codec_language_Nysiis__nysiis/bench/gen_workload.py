import random, sys, os
TOKENS = ['mac', 'kn', 'k', 'ph', 'pf', 'sch', 'ee', 'ie', 'dt', 'rt', 'rd', 'nt', 'nd', 'a', 'e', 'i', 'o', 'u', 'y', 'ev', 'ew', 'w', 'h', 'q', 'z', 'm', 'n', 's', 'l', 'r', 'b', 'c', 'd', 'f', 'g', 'j', 'p', 't', 'v', 'x', 'ay', 'aa']
EXTRA = ['', 'Macintosh', 'Knight', 'Phillips', 'Schmidt', 'Bobbie', 'Bartholomew', 'Meier', 'Johnston', "O'Brien", 'Smith-Jones', '  trim me ', 'Kennedy', 'Pfeiffer', 'Hanna', 'Dwight', 'Sally', 'Boyds', '123', 'Äpfel', 'Walt', 'Ray']
SEEDBASE = 20190722
# size -> (number of strings, token count per string)
SIZES = {"S": (80, 4), "M": (300, 30), "L": (700, 400)}
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
