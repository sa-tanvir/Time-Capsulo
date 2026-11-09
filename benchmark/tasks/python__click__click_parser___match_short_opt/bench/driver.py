"""Bench driver for click.parser.OptionParser._match_short_opt. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
import click
from click.parser import OptionParser, ParsingState
from click.exceptions import UsageError


def build(c):
    ctx = None
    if c["ctx"]:
        ctx = click.Context(click.Command("cli"), info_name="cli",
                            token_normalize_func=(lambda s: s.lower()) if c["lower"] else None)
    p = OptionParser(ctx)
    p.ignore_unknown_options = c["ignore"]
    for name, dest, action, nargs in c["opts"]:
        const = ("const", dest) if action.endswith("_const") else None
        p.add_option([name], dest, action=action, nargs=nargs, const=const)
    return p


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        data = json.load(fh)
    cases = [(build(c), c["rargs"], c["tokens"]) for c in data["cases"]]
    if mode == "check":
        h = hashlib.sha256()
        for p, rargs, tokens in cases:
            st = ParsingState(list(rargs))
            for tok in tokens:
                before = list(st.rargs)
                try:
                    p._match_short_opt(tok, st)
                    out = "ok %r %r" % (st.rargs, st.largs)
                except UsageError as e:
                    out = "ERR %s %s %r %r" % (type(e).__name__, e.format_message(), e.option_name, e.ctx is p.ctx)
                    st.rargs[:] = before   # remaining args after a failed match are not part of the contract
                h.update(out.encode() + b"\n")
            h.update(repr((sorted(st.opts.items()), st.order)).encode() + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    el, acc = 0.0, 0
    for _ in range(repeat):
        states = [ParsingState(list(rargs)) for _, rargs, _ in cases]   # fresh state per case, untimed
        t0 = time.perf_counter()
        for (p, _, tokens), st in zip(cases, states):
            m = p._match_short_opt
            for tok in tokens:
                try:
                    m(tok, st)
                except UsageError:
                    acc += 1
        el += time.perf_counter() - t0
        acc += sum(len(s.order) for s in states)
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
