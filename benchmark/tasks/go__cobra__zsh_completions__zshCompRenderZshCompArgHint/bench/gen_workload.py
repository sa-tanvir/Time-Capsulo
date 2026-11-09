"""Seeded workload generator for cobra.zshCompRenderZshCompArgHint. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

FILE = "cobra_annotations_zsh_completion_argument_file_completion"
WORD = "cobra_annotations_zsh_completion_argument_word_completion"
# (cases, max options per case)
SIZES = {"S": (4000, 4), "M": (1000, 40), "L": (100, 400)}
EDGE = [[1, FILE, ["*.log"]], [2, FILE, []], [1, WORD, ["word1", "word2"]],
        [1, WORD, ["single", "multiple words"]], [4, WORD, ['a"b', "c\\d", "tab\there", "été"]],
        [1, WORD, []], [3, "", ["x"]], [1, "cobra_annotations_zsh_dirname", []], [7, "bogus", None],
        [0, FILE, ["*"]], [12, FILE, ["*.txt", "*.md"]]]
TOKS = ["pod", "node", "svc", "my file", "a\"q", "*.go", "*.[ch]", "x\\y", "über", "dir/*.txt", "-flag"]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for k, (size, (n, mx)) in enumerate(SIZES.items()):
        rng = random.Random(20190607 + k)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            r = rng.random()
            tipe = FILE if r < 0.45 else WORD if r < 0.97 else "unknown"
            opts = [rng.choice(TOKS) + str(rng.randrange(100)) for _ in range(rng.randint(mx // 2, mx))]
            cases.append([rng.randint(1, 20), tipe, opts])
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
