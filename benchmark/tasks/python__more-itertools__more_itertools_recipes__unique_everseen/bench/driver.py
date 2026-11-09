"""Bench driver for unique_everseen(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from more_itertools.recipes import unique_everseen

KEYS = {None: None, "lower": str.lower, "tuple": tuple, "mod": lambda x: x % 97}

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [(c["data"], KEYS[c["key"]]) for c in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for data, key in cases:
            h.update(repr(list(unique_everseen(iter(data), key))).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for data, key in cases:
            acc += len(list(unique_everseen(iter(data), key)))
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))

if __name__ == "__main__":
    main()
