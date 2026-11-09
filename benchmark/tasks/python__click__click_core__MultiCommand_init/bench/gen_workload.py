"""Seeded workload generator for MultiCommand.__init__. Usage: python3 gen_workload.py <out_dir>

Per-case scale grows ~10x per size: each constructed multi command carries ~10 (S), 100 (M) or
1000 (L) parameters (options and positional arguments)."""
import json, random, sys
from pathlib import Path

SIZES = {"S": (10, 1000), "M": (100, 1000), "L": (1000, 1000)}   # (params per command, cases)
N_LISTS = 16


def param_list(rng, n, bad):
    ps = []
    for k in range(n):
        if rng.random() < 0.6:
            ps.append(["opt", "--o%d" % k])
        else:
            ps.append(["arg", "a%d" % k, rng.choice([True, None]), rng.choice([1, 1, 2])])
    if bad:   # one optional argument somewhere (explicit required=False or nargs=-1 without required)
        pos = rng.randrange(n)
        ps[pos] = ["arg", "a%d" % pos, False, 1] if rng.random() < 0.5 else ["arg", "a%d" % pos, None, -1]
    return ps


def case(rng):
    c = {"list": rng.randrange(N_LISTS), "name": rng.choice([None, "cli", "grp", "tool"])}
    c["chain"] = rng.random() < 0.75
    for k, choices in (("invoke_without_command", [None, True, False]),
                       ("no_args_is_help", [None, None, True, False]),
                       ("subcommand_metavar", [None, None, "", "SUB", "CMD [ARGS]..."]),
                       ("result_callback", [None, None, "cb"]),
                       ("help", [None, "Group help.", "Short\fhidden part"]),
                       ("hidden", [None, True])):
        v = rng.choice(choices)
        if v is not None:
            c[k] = v
    return c


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, cases)) in enumerate(SIZES.items()):
        rng = random.Random(20180926 + i)
        lists = [param_list(rng, n, bad=(j % 4 == 3)) for j in range(N_LISTS)]
        data = {"lists": lists, "cases": [case(rng) for _ in range(cases)]}
        (out_dir / f"workload_{size}.json").write_text(json.dumps(data))
