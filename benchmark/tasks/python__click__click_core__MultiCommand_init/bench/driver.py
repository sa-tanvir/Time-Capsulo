"""Bench driver for click.MultiCommand.__init__. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
import click


def cb(*a, **kw):
    return a


def build_params(spec):
    out = []
    for p in spec:
        if p[0] == "opt":
            out.append(click.Option([p[1]]))
        else:
            kw = {"nargs": p[3]}
            if p[2] is not None:
                kw["required"] = p[2]
            out.append(click.Argument([p[1]], **kw))
    return out


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        data = json.load(fh)
    lists = [build_params(s) for s in data["lists"]]
    cases = []
    for c in data["cases"]:
        kw = {k: v for k, v in c.items() if k not in ("list", "name")}
        if kw.get("result_callback") == "cb":
            kw["result_callback"] = cb
        kw["params"] = lists[c["list"]]
        cases.append((c["name"], kw))
    MC = click.MultiCommand
    if mode == "check":
        h = hashlib.sha256()
        for name, kw in cases:
            try:
                m = MC(name, **kw)
                out = repr((m.name, m.no_args_is_help, m.invoke_without_command, m.subcommand_metavar, m.chain,
                            m.result_callback is cb, m.result_callback is None, m.params is kw["params"],
                            len(m.params), m.help, m.hidden, m.callback, m.allow_extra_args,
                            m.allow_interspersed_args, m.context_settings))
            except RuntimeError as e:
                out = "ERR %s %s" % (type(e).__name__, e)
            h.update(out.encode() + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for name, kw in cases:
            try:
                MC(name, **kw)
                acc += 1
            except RuntimeError:
                acc += 2
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
