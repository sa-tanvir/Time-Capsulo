"""Bench driver for Option.get_help_record. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, random, sys, time
import click


def build(o):
    kw = {"help": o["help"], "hidden": o["hidden"], "required": o["required"],
          "show_default": o["show_default"], "show_envvar": o["show_envvar"],
          "envvar": o["envvar"], "allow_from_autoenv": o["allow_from_autoenv"]}
    kind = o["kind"]
    rng = random.Random(o["seed"])
    if kind in ("flag",):
        kw["is_flag"] = True
    elif kind == "count":
        kw["count"] = True
        if o["default"] == "scalar":
            kw["default"] = rng.randint(0, 3)
    elif kind == "value":
        t = o["type"]
        typ = {None: None, "int": int, "float": float, "path": click.Path(),
               "intrange": click.IntRange(0, 10)}.get(t) if t != "choice" else click.Choice(o["choices"])
        nargs = o["nargs"]
        if nargs != 1 and typ is None:
            typ = str
        kw.update(type=typ, nargs=nargs, multiple=o["multiple"], metavar=o["metavar"])
        d = o["default"]
        if d == "dyn":
            kw["default"] = lambda: 1
        elif d in ("scalar", "list"):
            if t == "choice":
                vals = o["choices"]
            elif t in ("int", "intrange"):
                vals = [0, 1, 7, 10]
            elif t == "float":
                vals = [0.5, 1.25, 3.0]
            else:
                vals = ["foo", "bar", "", "x y"]
            if d == "list" or nargs != 1:
                kw["default"] = tuple(rng.choice(vals) for _ in range(nargs if nargs != 1 else rng.randint(0, o.get("k", 3))))
            else:
                kw["default"] = rng.choice(vals)
    return click.Option(o["decls"], **kw)


def load(size):
    with open(f"/task/bench/workload_{size}.json") as fh:
        data = json.load(fh)
    cmd = click.Command("cli")
    ctxs = {p: click.Context(cmd, info_name="cli", auto_envvar_prefix=p) for p in (None, "APP", "TEST")}
    pairs = [(build(o), ctxs[o["ctx_prefix"]]) for o in data["options"]]
    return pairs * data["passes"]


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    cases = load(size)
    if mode == "check":
        h = hashlib.sha256()
        for opt, ctx in cases:
            h.update(repr(opt.get_help_record(ctx)).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for opt, ctx in cases:
            if opt.get_help_record(ctx) is not None:
                acc += 1
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
