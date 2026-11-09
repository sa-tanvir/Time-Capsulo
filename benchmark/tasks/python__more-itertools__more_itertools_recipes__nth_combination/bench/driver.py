"""Bench driver for nth_combination(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from more_itertools.recipes import nth_combination

def call(pool, r, index):
    try:
        return nth_combination(pool, r, index)
    except (ValueError, IndexError) as e:
        return type(e).__name__

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [(tuple(range(c["n"])), c["r"], int(c["index"])) for c in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for c in cases:
            h.update(repr(call(*c)).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for c in cases:
            acc += len(call(*c))
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))

if __name__ == "__main__":
    main()
