"""Bench driver for replace(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from more_itertools.more import replace

def make_pred(kind, arg):
    if kind == "member":
        s = frozenset(arg)
        return lambda x: x in s
    if kind == "pattern":
        t = tuple(arg)
        return lambda *a: a == t
    return lambda *a: a[0] == arg

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [(c["seq"], make_pred(c["kind"], c["arg"]), tuple(c["subs"]), c["count"], c["w"])
                 for c in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for seq, pred, subs, count, w in cases:
            h.update(repr(list(replace(seq, pred, subs, count=count, window_size=w))).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for seq, pred, subs, count, w in cases:
            acc += len(list(replace(seq, pred, subs, count=count, window_size=w)))
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))

if __name__ == "__main__":
    main()
