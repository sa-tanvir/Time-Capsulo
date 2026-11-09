import random, sys, os
SEEDBASE = 20190831
SIZES = {"S": (60, 8), "M": (200, 400), "L": (100, 60000)}
WS = [" ", "  ", " \t"[0], " "]
def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, ln = SIZES[size]
        rows = []
        if size == "S":
            for p in ["0}", "1,number}", "12 ,x}", " 7 }", "  5}", "3", "}", ",", "a}", "1a}", "1 2}", "12", "x1}", "99999999999}",
                      "{0}", "-1}", "007}", "5,"]:
                rows.append((0, p))
            rows.append((3, "ab 4}")); rows.append((2, "ab 4}"))
        while len(rows) < count:
            kind = rng.random()
            lead = " " * rng.randint(0, ln // 4 if size != "S" else 3)
            digs = "".join(rng.choice("0123456789") for _ in range(rng.randint(1, ln // 2 if size != "S" else 5)))
            if kind < 0.35:
                p = lead + digs + rng.choice(["}", ",", " }", " ,x}", "  ,x}"]) + "tail"
            elif kind < 0.5:
                p = lead + digs
            elif kind < 0.65:
                p = lead + digs + rng.choice("abx;") + digs + "}"
            elif kind < 0.8:
                p = lead + digs[:len(digs)//2] + " " + digs[len(digs)//2:] + "}"
            elif kind < 0.9:
                p = lead + digs + " " * rng.randint(1, 4) + "}"
            else:
                p = "pre" + lead + digs + "}"
            start = 3 if p.startswith("pre") else (rng.choice([0, 0, 0, 1]) if size == "S" else 0)
            start = min(start, len(p))
            rows.append((start, p))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join("%d\t%s" % r for r in rows) + "\n")
main(sys.argv[1])
