"""Bench driver for click._bashcomplete.add_subcommand_completions. argv: <size> <repeat> <mode>"""
import hashlib, json, sys, time
from click._bashcomplete import add_subcommand_completions, resolve_ctx
from clis import build_all, build_big


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        data = json.load(fh)
    trees = build_all()
    trees["big"] = build_big(data["big_n"])
    base = [(resolve_ctx(trees[q["tree"]], "prog", list(q["args"])), q["incomplete"]) for q in data["queries"]]
    cases = base * data["passes"]
    if mode == "check":
        h = hashlib.sha256()
        for ctx, inc in cases:
            out = [("seed", None)]
            r = add_subcommand_completions(ctx, inc, out)
            h.update(repr((r, out)).encode() + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for ctx, inc in cases:
            out = []
            add_subcommand_completions(ctx, inc, out)
            acc += len(out)
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
