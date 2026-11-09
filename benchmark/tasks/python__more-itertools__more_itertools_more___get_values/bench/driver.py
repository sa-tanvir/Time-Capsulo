"""Bench driver for bucket._get_values (reached through bucket.__getitem__). argv: <size> <repeat> <mode>"""
import hashlib, json, sys, time
from itertools import islice
from more_itertools.more import bucket

def run(c):
    k = c["k"]
    validator = (lambda v: v % 2 == 1) if c["valid_odd_only"] else None
    D = bucket(c["data"], key=lambda x: x % k, validator=validator)
    children = {}
    out = []
    for b, how in c["plan"]:
        if how == -2:
            out.append(b in D)
            continue
        it = children.get(b)
        if it is None:
            it = children[b] = D[b]
        out.append(list(it) if how == -1 else list(islice(it, how)))
    return out, D

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for c in cases:
            out, D = run(c)
            pending = sorted((key, list(q)) for key, q in D._cache.items() if q)
            h.update(repr((out, pending)).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for c in cases:
            acc += len(run(c)[0])
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))

if __name__ == "__main__":
    main()
