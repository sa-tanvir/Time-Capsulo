"""Bench driver for roundrobin(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from more_itertools.recipes import roundrobin

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        # case = list of input lengths; input j holds values j*1_000_000 + 0..len-1 (so origin is visible)
        cases = [[list(range(j * 1_000_000, j * 1_000_000 + n)) for j, n in enumerate(lens)]
                 for lens in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for lists in cases:
            h.update(repr(list(roundrobin(*[iter(l) for l in lists]))).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for lists in cases:
            acc += len(list(roundrobin(*lists)))
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))

if __name__ == "__main__":
    main()
