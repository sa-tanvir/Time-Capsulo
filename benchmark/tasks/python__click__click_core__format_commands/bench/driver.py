"""Bench driver for MultiCommand.format_commands. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
import click
from click.formatting import HelpFormatter


class ListedMulti(click.MultiCommand):
    """Multi command with an explicit listing order that may contain unknown or duplicate names."""

    def __init__(self, listed, table):
        click.MultiCommand.__init__(self, "cli")
        self.listed = listed
        self.table = table

    def list_commands(self, ctx):
        return list(self.listed)

    def get_command(self, ctx, name):
        return self.table.get(name)


def build(c):
    listed, table = [], {}
    for e in c["entries"]:
        listed.append(e["name"])
        k = e["kind"]
        if k == "ghost":
            continue
        if k == "hidden_group":
            g = click.Group(e["name"], hidden=True)
            g.add_command(click.Command("nope", help="inner"))
            table[e["name"]] = g
            continue
        cname = ("x" + e["name"]) if e.get("alias") else e["name"]
        table[e["name"]] = click.Command(cname, help=e["help"], short_help=e["short_help"], hidden=(k == "hidden"))
    mc = ListedMulti(listed, table)
    return mc, click.Context(mc, info_name="cli"), c["width"]


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [build(c) for c in json.load(fh)["cases"]]
    if mode == "check":
        h = hashlib.sha256()
        for mc, ctx, width in cases:
            f = HelpFormatter(width=width)
            r = mc.format_commands(ctx, f)
            h.update(repr((r, f.getvalue())).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    el = 0.0
    for _ in range(repeat):
        fmts = [HelpFormatter(width=w) for _, _, w in cases]   # fresh sinks, built outside the timed region
        t0 = time.perf_counter()
        for (mc, ctx, _), f in zip(cases, fmts):
            mc.format_commands(ctx, f)
        el += time.perf_counter() - t0
        acc += sum(len(f.buffer) for f in fmts)
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
