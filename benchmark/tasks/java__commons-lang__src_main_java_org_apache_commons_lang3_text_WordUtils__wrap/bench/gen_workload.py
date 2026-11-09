import random, sys, os
SEEDBASE = 20190411
# size -> (cases, words per base text, repetitions, wrapLength range)
SIZES = {"S": (80, 14, 1, (1, 30)), "M": (80, 600, 2, (15, 90)), "L": (14, 700, 120, (15, 100))}
LETTERS = "abcdefghijklmnopqrstuvwxyz"
# wrapOn -> separator strings used when generating text for it
STYLES = [(None, [" "]), (" ", [" ", "  "]), ("-", ["-", "--"]), (",", [",", ", "]), ("[ ,;]+", [" ", ", ", ";"]), ("", [" "]), ("  ", [" "]), ("[-/]", ["-", "/", " "])]

def esc(s):
    if s is None:
        return "<null>"
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, words, reps, wlr = SIZES[size]
        rows = []   # text, rep, wrapLength, newline, wrapLongWords, wrapOn
        if size == "S":
            rows += [
                (None, 1, 5, "\n", 0, " "), ("", 1, 5, "\n", 1, " "), ("Here is one line of text that is going to be wrapped after 20 columns.", 1, 20, "\n", 0, None),
                ("Here is one line of text that is going to be wrapped after 20 columns.", 1, 20, "<br />", 0, None),
                ("Click here to jump to the commons website - https://commons.apache.org", 1, 20, "\n", 0, None),
                ("Click here to jump to the commons website - https://commons.apache.org", 1, 20, "\n", 1, None),
                ("Click here, https://commons.apache.org, to jump to the commons website", 1, 20, "\n", 1, None),
                ("flammable/inflammable", 1, 30, "\n", 1, "/"), ("flammable/inflammable", 1, 6, "\n", 1, "/"), ("flammable/inflammable", 1, 6, "\n", 0, "/"),
                ("  leading and trailing  ", 1, 8, "\n", 0, None), ("  leading and trailing  ", 1, 8, "\n", 1, " "), ("a b c d e f", 1, 0, "\n", 1, " "),
                ("a b c d e f", 1, -5, "\n", 0, " "), ("a b c d e f", 1, 1, "|", 0, None), ("abcdefghij", 1, 3, "\n", 1, " "), ("abcdefghij", 1, 3, "\n", 0, " "),
                ("abc defghij klm", 1, 3, "\n", 0, " "), ("word", 1, 2147483647, "\n", 1, " "), ("a b", 1, 2147483647, "\n", 0, None),
                ("hello world", 1, 5, None, 0, " "), ("hello world foo", 1, 7, "\r\n", 1, " "), ("a,b,c,d", 1, 3, "\n", 0, ","), ("aa,,bb,,cc", 1, 3, "\n", 1, ",+"),
                ("a  b   c", 1, 2, "\n", 0, "  "), ("x y", 1, 5, "\n", 0, "("), ("this is a test string", 1, 4, "\n", 1, "\\s+"), ("two  spaces here", 1, 5, "\n", 0, "[ ]+"),
            ]
        while len(rows) < count:
            on, seps = rng.choice(STYLES)
            wl = rng.randint(*wlr)
            lw = rng.randint(0, 1)
            maxw = 10 if (size != "S" and not lw) else rng.choice([4, 12])
            ws = ["".join(rng.choice(LETTERS) for _ in range(rng.randint(1, maxw))) for _ in range(words)]
            t = ""
            for w in ws:
                t += w + rng.choice(seps)
            if rng.random() < 0.5:
                t = t.rstrip(" ,;-/")
            if rng.random() < 0.15:
                t = rng.choice(seps) + t
            nl = rng.choice(["\n", "\n", "\n", "<br />", "\r\n", "|", None])
            if on == "" and rng.random() < 0.5:
                on = None
            rows.append((t, reps, wl, nl, lw, on))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            for t, rp, wl, nl, lw, on in rows:
                f.write("\t".join([esc(t), str(rp), str(wl), esc(nl), str(lw), esc(on)]) + "\n")

main(sys.argv[1])
