"""Seeded workload generator for Option.get_help_record. Usage: python3 gen_workload.py <out_dir>

Per-case scale grows ~10x per size: each option has up to K extra declarations (aliases), env-var
lists and list defaults of up to K entries and help text of ~K words, with K = 2 (S), 20 (M), 200 (L)."""
import json, random, string, sys
from pathlib import Path

SIZES = {"S": (2, 1_000), "M": (20, 1_000), "L": (200, 1_000)}   # (K, options)
HELPS = [None, "", "Verbosity", "das foo", "Enables or disables debug mode.",
         "\n        hello\n\n        i am\n\n        multiline\n    ", "Path to the config file."]


def word(rng):
    return "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(1, 8)))


def option(rng, K):
    name = word(rng) + rng.choice(["", "_x", "-y"])
    kind = rng.choice(["value", "value", "value", "flag", "boolpair", "slashpair", "count"])
    o = {"decls": [], "kind": kind}
    short = rng.random() < 0.5
    extra = rng.randint(0, K)
    if kind == "slashpair":
        o["decls"] = ["/" + name + ";/no-" + name] + ["/%s%d;/no-%s%d" % (name, j, name, j) for j in range(extra)]
    elif kind == "boolpair":
        o["decls"] = (["-" + name[0]] if short else []) + ["--" + name + "/--no-" + name] + \
            ["--%s%d/--no-%s%d" % (name, j, name, j) for j in range(extra)]
        if rng.random() < 0.3:
            o["decls"].append(rng.choice(["-" + name[0].upper(), "/" + name[0]]))
    else:
        prefix = rng.choice(["--", "--", "--", "++", "-"])
        decls = [prefix + name] + ["%s%s-%d" % (prefix, name, j) for j in range(extra)]
        if short:
            decls.insert(rng.randint(0, 1), "-" + rng.choice(string.ascii_letters))
        if rng.random() < 0.1:
            decls.append("/" + name)
        o["decls"] = decls
    if kind == "value":
        o["type"] = rng.choice([None, None, "int", "float", "choice", "intrange", "path"])
        if o["type"] == "choice":
            o["choices"] = [word(rng) for _ in range(rng.randint(1, 4))]
        o["nargs"] = rng.choice([1, 1, 1, 1, 2])
        o["multiple"] = rng.random() < 0.2 and o["nargs"] == 1
        o["metavar"] = rng.choice([None] * 6 + ["NAME", "<file>"])
        d = rng.choice(["none", "none", "scalar", "dyn", "list"])
        if d == "list" and not o["multiple"] and o["nargs"] == 1:
            d = "scalar"
        o["default"] = d
    else:
        o["default"] = rng.choice(["missing", "missing", "scalar"]) if kind == "count" else "missing"
    o["help"] = rng.choice(HELPS)
    if o["help"] and rng.random() < 0.6:
        o["help"] += " " + " ".join(word(rng) for _ in range(rng.randint(0, K)))
    o["k"] = K
    o["hidden"] = rng.random() < 0.08
    o["required"] = rng.random() < 0.2
    o["show_default"] = rng.choice([False, True, True, "current user", "", "from config"])
    o["show_envvar"] = rng.random() < 0.4
    o["envvar"] = rng.choice([None, None, "ENV_" + name.upper().replace("-", "_"),
                              ["E%d_%s" % (j, name.upper()) for j in range(rng.randint(1, K + 1))]])
    o["allow_from_autoenv"] = rng.random() < 0.8
    o["ctx_prefix"] = rng.choice([None, "APP", "TEST"])
    o["seed"] = rng.randint(0, 10**6)
    return o


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (K, n)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        data = {"passes": 1, "options": [option(rng, K) for _ in range(n)]}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(data))
