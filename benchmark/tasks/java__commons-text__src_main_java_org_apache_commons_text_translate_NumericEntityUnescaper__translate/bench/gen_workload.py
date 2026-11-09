import random, sys, os
SEEDBASE = 20190831
# size -> (strings, tokens per string)
SIZES = {"S": (30, 8), "M": (60, 600), "L": (40, 8000)}
TOKENS = ["a", "b", "z", " ", "x", "&", "&#", "&#x", "&#X", "&#;", "&#x;", "&#65", "&#65;", "&#x41;", "&#X7a;", "&#x1F600;",
          "&#68642;", "&#12ab;", "&#99999999999;", "&#1114112;", "&#xAbCdEf;", "&#xZZ;", "&#0;", "&#8364;", "&#xe9", "&amp;",
          "&#00065;", "&#38;", "&#x26", "&#1;", "#", ";", "&#xD83D;", "&#xDE00;"]
EDGE = ["", "&", "&#", "&#1", "&#x", "&#x1", "&#65;", "&#65", "&#x41;", "&#x41", "&#x;", "&#;", "&#68642;", "&#1114112;", "x&#"]

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, ntok = SIZES[size]
        lines = list(EDGE) if size == "S" else []
        while len(lines) < count:
            n = rng.randint(max(1, ntok // 2), ntok)
            lines.append("".join(rng.choice(TOKENS) for _ in range(n)))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

main(sys.argv[1])
