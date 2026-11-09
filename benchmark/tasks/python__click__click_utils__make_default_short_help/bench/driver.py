"""Bench driver for click.utils.make_default_short_help. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from click.utils import make_default_short_help


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [tuple(c) for c in json.load(fh)["cases"]]
    if mode == "check":
        h = hashlib.sha256()
        for text, ml in cases:
            h.update(repr(make_default_short_help(text, ml)).encode())
            h.update(b"\0")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for text, ml in cases:
            acc += len(make_default_short_help(text, ml))
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
