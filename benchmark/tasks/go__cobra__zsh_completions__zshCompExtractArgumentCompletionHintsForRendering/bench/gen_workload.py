"""Seeded workload generator for cobra.zshCompExtractArgumentCompletionHintsForRendering.
Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

FILE = "cobra_annotations_zsh_completion_argument_file_completion"
WORD = "cobra_annotations_zsh_completion_argument_word_completion"
# (cases, max positions, max options)
SIZES = {"S": (2000, 3, 3), "M": (300, 30, 10), "L": (30, 300, 30)}

def hint(t, opts):
    return {"type": t, "options": opts}

# each case: [annotation JSON string or null, ValidArgs]
EDGE = [[None, []], [json.dumps({"1": hint(FILE, ["*.log"]), "2": hint(FILE, [])}), []],
        [json.dumps({"1": hint(WORD, ["word1", "word2"])}), []], [None, ["word1", "word2"]],
        [json.dumps({"2": hint(FILE, None)}), ["word1", "word2"]], [json.dumps({"1": hint(FILE, ["*.txt"])}), ["a"]],
        [json.dumps({"2": hint(WORD, ["x"]), "10": hint(FILE, [])}), []], [json.dumps({"3": hint("bogus", [])}), ["a"]],
        ["not json", []], [json.dumps({}), ["only valid"]]]
TOKS = ["pod", "node", "svc", "my file", 'q"t', "*.go", "über", "dir/*.txt"]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for k, (size, (n, mpos, mopt)) in enumerate(SIZES.items()):
        rng = random.Random(20190607 + k)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            ann = {}
            for p in rng.sample(range(1, mpos * 2 + 2), rng.randint(0, mpos)):
                t = FILE if rng.random() < 0.5 else WORD
                ann[str(p)] = hint(t, [rng.choice(TOKS) + str(rng.randrange(99)) for _ in range(rng.randint(0, mopt))])
            if rng.random() < 0.02:
                ann[str(mpos * 3)] = hint("unknown", [])
            va = [rng.choice(TOKS) for _ in range(rng.randint(0, mopt))] if rng.random() < 0.6 else []
            cases.append([json.dumps(ann) if ann or rng.random() < 0.5 else None, va])
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
