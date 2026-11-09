import random, sys, os
SEEDBASE = 20190411
# size -> (cases, items in the base format, repetitions)
SIZES = {"S": (80, 10, 1), "M": (80, 400, 3), "L": (40, 2500, 80)}

def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")

LET = "yMdHmsS"
PUNCT = list(" :.-/TPZ_W,;D") + ["Y", "m1", "ab", "T "]
QUOTED = ["days", "'", "y", "M", "d H m s S", ":", "", " and ", "PT", "Z"]

def fmt(rng, items):
    parts = []
    for _ in range(items):
        r = rng.random()
        if r < 0.40:
            parts.append(rng.choice(LET) * rng.randint(1, 4))
        elif r < 0.65:
            parts.append(rng.choice(PUNCT))
        elif r < 0.85:
            q = rng.choice(QUOTED)
            if q == "'":
                parts.append("''")
            else:
                parts.append("'" + q + "'")
        else:
            parts.append(rng.choice(LET))
    return "".join(parts)

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, items, reps = SIZES[size]
        rows = []   # format, rep
        if size == "S":
            rows += [("yMdHmsS", 1), ("HH:mm:ss.SSS", 1), ("'P'yyyy'Y'M'M'd'DT'H'H'm'M's.SSS'S'", 1), ("", 1), ("d", 1), ("dd", 1), ("ddd d", 1),
                     ("'", 1), ("'abc", 1), ("abc'", 1), ("''", 1), ("a''b", 1), ("'a''b'", 1), ("'a'b'c'", 1), ("y'x'y", 1), ("yy'a'y", 1), ("y M'a'M y", 1),
                     ("d 'days' H 'hours'", 1), ("'yMdHmsS'", 1), ("xyzzy", 1), ("yyyy-MM-dd'T'HH:mm:ss", 1), ("'unterminated y", 1), ("y'' M", 1), ("H'm'H'm'", 1),
                     ("ss.SSS", 1), ("Y m D", 1), ("'' ''", 1), ("'a", 1), ("''''", 1), ("'''", 1)]
        while len(rows) < count:
            f = fmt(rng, items)
            if size == "S" and rng.random() < 0.1:
                f += "'" + f[:3]
            rows.append((f, reps))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            for t, rp in rows:
                f.write("\t".join([esc(t), str(rp)]) + "\n")

main(sys.argv[1])
