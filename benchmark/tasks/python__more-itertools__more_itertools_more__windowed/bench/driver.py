"""Bench driver for windowed(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from more_itertools.more import windowed

def run(c):
    return list(windowed(c["seq"], c["n"], fillvalue=c["fillvalue"], step=c["step"]))

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for c in cases:
            h.update(repr(run(c)).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    t0 = time.perf_counter()
    for _ in range(repeat):
        for c in cases:
            run(c)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": time.perf_counter() - t0}))

if __name__ == "__main__":
    main()
