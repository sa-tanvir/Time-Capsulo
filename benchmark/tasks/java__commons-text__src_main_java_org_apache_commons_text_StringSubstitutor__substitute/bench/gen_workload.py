import random, sys, os
SEEDBASE = 20190831
# size -> (templates, tokens per template)
SIZES = {"S": (50, 10), "M": (60, 250), "L": (30, 1800)}
WORDS = ["alpha", "beta", "x", "the", "quick", "fox", "$", "{", "}", "a:b", ":-", "-", " ", " ", " ", "dollar$", "$$", "\\", "ok."]
def var(rng):
    r = rng.random()
    k = rng.randrange(30)
    if r < 0.50:
        return "${v%d}" % k
    if r < 0.58:
        return "${nokey}"
    if r < 0.66:
        return "${nokey:-dflt%d}" % k
    if r < 0.70:
        return "${nokey:-${v%d}}" % rng.randrange(10)
    if r < 0.76:
        return "$${v%d}" % k
    if r < 0.82:
        return "${v${n%d}}" % rng.randrange(3)
    if r < 0.86:
        return "${v%d:-fallback}" % k
    if r < 0.89:
        return "${v1${n0}}"
    if r < 0.92:
        return "${v%d" % k            # unterminated
    if r < 0.94:
        return "${}"
    if r < 0.96:
        return "$${nokey:-z}"
    return "${w%d}" % rng.randrange(3)

EDGE = ["", "no variables here", "${v1}", "${v1}${v2}", "$${v1}", "$$${v1}", "${nokey}", "${nokey:-d}", "${n0}", "${v${n0}}", "${v${n1}}x",
        "${cycA}", "${cycB}", "${v26}", "${v27}", "pre ${v10} post ${v11}", "${v1", "${", "$", "}", "${${v1}}", "${nokey:-${nokey2:-deep}}",
        "${v1:-x}", "${:-x}", "${ v1 }", "a${v1}b${v2}c${v3}d", "${v28}", "${v29}", "${w0}", "$${v10}${v10}"]

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, ntok = SIZES[size]
        lines = list(EDGE) if size == "S" else []
        while len(lines) < count:
            n = rng.randint(max(1, ntok // 2), ntok)
            parts = []
            for _ in range(n):
                parts.append(var(rng) if rng.random() < 0.45 else rng.choice(WORDS))
            lines.append("".join(parts))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

main(sys.argv[1])
