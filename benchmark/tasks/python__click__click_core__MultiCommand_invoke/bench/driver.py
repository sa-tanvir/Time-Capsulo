"""Bench driver for click.MultiCommand.invoke. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
import click

LOG = []


def make_group(name, chain=False, iwc=False, rc=False, with_arg=False):
    def cb(ctx, debug, **kw):
        ctx.obj = {"debug": debug, "seen": ctx.invoked_subcommand}
        LOG.append(("grp", name, ctx.invoked_subcommand, tuple(ctx.args), tuple(ctx.protected_args), debug))
        return ("grp", name, debug)
    params = [click.Option(["--debug/--no-debug"], default=False)]
    if with_arg:
        params.append(click.Argument(["obj"]))
    g = click.Group(name, callback=click.pass_context(cb), params=params, chain=chain,
                    invoke_without_command=iwc, no_args_is_help=False)
    if rc:
        def result(value, debug, **kw):
            LOG.append(("rc", name))
            return ("rc", name, len(value) if isinstance(value, list) else value, debug)
        g.result_callback = result

    @g.command("a")
    @click.pass_context
    def a(ctx):
        return ("a", ctx.obj["debug"])

    @g.command("b")
    @click.option("--format", default="none")
    def b(format):
        return ("b", format)

    @g.command("c")
    @click.argument("value")
    def c(value):
        return ("c", value)

    @g.command("collect")
    @click.argument("vals", nargs=-1)
    @click.pass_context
    def collect(ctx, vals):
        return ("collect", len(vals), vals[:1], ctx.obj["seen"])

    @g.command("sync")
    def sync():
        return "sync"
    return g


GROUPS = {
    "chain": make_group("chain", chain=True),
    "chain_rc": make_group("chain_rc", chain=True, rc=True),
    "chain_iwc": make_group("chain_iwc", chain=True, iwc=True, rc=True),
    "single": make_group("single"),
    "single_rc": make_group("single_rc", rc=True),
    "single_iwc": make_group("single_iwc", iwc=True),
    "withobj": make_group("withobj", with_arg=True),
}


def prepare(cases):
    """Fresh, parsed contexts (untimed). Cases whose own command line fails to parse yield None."""
    out = []
    for g, toks in cases:
        try:
            out.append((g, g.make_context(g.name, list(toks))))
        except (click.ClickException, click.exceptions.Exit):
            out.append((g, None))
    return out


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        data = json.load(fh)
    cases = [(GROUPS[g], toks) for g, toks in data["cases"]]
    if mode == "check":
        h = hashlib.sha256()
        for g, ctx in prepare(cases):
            del LOG[:]
            if ctx is None:
                out = "PREP"
            else:
                try:
                    rv = g.invoke(ctx)
                    out = "ok %r" % (rv,)
                except click.ClickException as e:
                    out = "ERR %s %s" % (type(e).__name__, e.format_message())
                out += " %r %r %r" % (ctx.invoked_subcommand, ctx.args, ctx.protected_args)
            h.update((out + repr(LOG)).encode() + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    el, acc = 0.0, 0
    for _ in range(repeat):
        prepared = [(g, ctx) for g, ctx in prepare(cases) if ctx is not None]
        del LOG[:]
        t0 = time.perf_counter()
        for g, ctx in prepared:
            try:
                g.invoke(ctx)
                acc += 1
            except click.ClickException:
                acc += 2
        el += time.perf_counter() - t0
        acc += len(LOG)
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
