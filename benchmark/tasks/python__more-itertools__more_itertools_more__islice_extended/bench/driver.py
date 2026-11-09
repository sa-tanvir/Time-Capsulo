"""Bench driver for islice_extended(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from more_itertools.more import islice_extended

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        raw = json.load(fh)
    # inputs are one-shot iterators over prebuilt lists (built outside the timed loop)
    cases = [(list(range(c["len"])), c["args"]) for c in raw]
    if mode == "check":
        h = hashlib.sha256()
        for seq, args in cases:
            h.update(repr(list(islice_extended(iter(seq), *args))).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for seq, args in cases:
            acc += len(list(islice_extended(iter(seq), *args)))
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))

if __name__ == "__main__":
    main()
