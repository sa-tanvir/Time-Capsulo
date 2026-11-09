import random, sys, os
SEEDBASE = 20190722
TOKENS = ["a","e","i","o","u","ch","sch","sh","tsch","th","ph","gh","ck","cz","sz","zh","ski","wicz","ov","off","ez","ez","ian","mann","berg","stein","man","son","sen","ez","ini","elli","ero","aux","eau","ois","ij","ue","ae","oe","b","c","d","f","g","h","j","k","l","m","n","p","r","s","t","v","w","z","x","y","q"]
PREFIXES = ["de la ", "van ", "ben ", "al ", "bar ", "d'", "ibn ", "von ", "bat ", "el ", "di ", "da "]
# size -> (cases, max tokens per word)
SIZES = {"S": (80, 5), "M": (50, 14), "L": (40, 70)}
NAMETYPES = ["GENERIC", "ASHKENAZI", "SEPHARDIC"]
RULETYPES = ["APPROX", "EXACT"]

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, ntok = SIZES[size]
        lines = []
        for k in range(count):
            w = "".join(rng.choice(TOKENS) for _ in range(rng.randint(2, ntok)))
            r = rng.random()
            if r < 0.15:
                w = rng.choice(PREFIXES) + w
            elif r < 0.25:
                w = w + " " + "".join(rng.choice(TOKENS) for _ in range(rng.randint(2, ntok)))
            elif r < 0.3:
                w = w.capitalize() + "-" + w
            nt = NAMETYPES[k % 3]
            rt = RULETYPES[(k // 3) % 2]
            concat = rng.randint(0, 1)
            anylang = 1 if rng.random() < 0.2 else 0
            lines.append("%s %s %d %d %s" % (nt, rt, concat, anylang, w))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

main(sys.argv[1])
