"""Seeded workload generator for doc.indentString. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, approx bytes per case)
SIZES = {"S": (2000, 60), "M": (200, 6000), "L": (20, 120000)}
EDGE = [["", "  "], ["abc", "  "], ["a\nb", "  "], ["a\nb\n", "> "], ["a\n\nb", "--"], ["\nx", "#"],
        ["\n\n", "#"], [" \n\r\n", "#"], ["line1\nline2", ""], ["héllo\nwörld\n", "» "], ["\n", ""]]
PREFIXES = ["  ", "\t", "> ", "", "    ", "│ "]
WORDS = ["cobra", "run", "--flag", "echo", "times", "x", "kubectl get pods", "été", "#", "  "]

def text(rng, target):
    parts, n = [], 0
    while n < target:
        r = rng.random()
        if r < 0.15:
            piece = "\n"
        elif r < 0.2:
            piece = "\n\n"
        else:
            piece = rng.choice(WORDS) + " "
        parts.append(piece)
        n += len(piece)
    return "".join(parts)

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, approx)) in enumerate(SIZES.items()):
        rng = random.Random(20190607 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append([text(rng, rng.randint(approx // 2, approx * 3 // 2)), rng.choice(PREFIXES)])
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
