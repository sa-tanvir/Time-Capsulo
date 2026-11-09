"""Seeded workload generator for cobra.zshCompGenFlagEntryExtras. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

EXT = "cobra_annotation_bash_completion_filename_extensions"
DIR = "cobra_annotations_zsh_dirname"
# (cases, max patterns, max unrelated annotation keys)
SIZES = {"S": (5000, 3, 2), "M": (2000, 30, 8), "L": (200, 300, 40)}
EDGE = [["true", None], ["true", {EXT: ["*.go"]}], ["", None], ["", {}], ["", {"other": ["x"]}],
        ["", {EXT: []}], ["", {EXT: ["*.log", "*.txt"]}], ["", {DIR: ["-(/)"]}],
        ["", {DIR: ['a"b', "ignored"]}], ["false", {DIR: ["-(/)"]}]]
PATS = ["*.log", "*.txt", "*.go", "*.[ch]", "*.tar.gz", "my dir/*", "é*.md", "*"]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for k, (size, (n, mp, mk)) in enumerate(SIZES.items()):
        rng = random.Random(20190607 + k)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            noopt = "true" if rng.random() < 0.15 else ""
            ann = {}
            for j in range(rng.randint(0, mk)):
                ann["cobra_annotation_bash_completion_custom_%d" % j] = ["__f%d" % j]
            r = rng.random()
            if r < 0.6:
                ann[EXT] = [rng.choice(PATS) + str(rng.randrange(50)) for _ in range(rng.randint(mp // 2, mp))]
            elif r < 0.85:
                ann[DIR] = [rng.choice(["-(/)", "*(/)", 'q"d'])]
            cases.append([noopt, ann])
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
