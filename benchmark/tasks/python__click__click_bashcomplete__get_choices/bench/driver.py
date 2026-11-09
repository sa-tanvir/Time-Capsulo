"""Bench driver for click._bashcomplete.get_choices. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from click._bashcomplete import get_choices
from clis import build_all


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        raw = json.load(fh)
    trees = build_all()
    cases = [(trees[c["tree"]], c["args"], c["incomplete"]) for c in raw]
    if mode == "check":
        h = hashlib.sha256()
        for cli, args, inc in cases:
            try:
                out = repr(get_choices(cli, "prog", list(args), inc))
            except Exception as e:  # noqa
                out = "ERR " + type(e).__name__
            h.update(out.encode() + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    arg_lists = [[list(a) for _, a, _ in cases] for _ in range(repeat)]
    acc = 0
    t0 = time.perf_counter()
    for r in range(repeat):
        lists = arg_lists[r]
        for i, (cli, _, inc) in enumerate(cases):
            acc += len(get_choices(cli, "prog", lists[i], inc))
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
