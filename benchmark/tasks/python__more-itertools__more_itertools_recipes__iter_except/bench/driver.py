"""Bench driver for iter_except(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from collections import deque
from more_itertools.recipes import iter_except

RAISES = {"pop": IndexError, "popleft": IndexError, "next": StopIteration}
EXC = {"exact": lambda e: e, "base": lambda e: Exception, "tuple": lambda e: (KeyError, e),
       "wrong": lambda e: KeyError}

def setup(c):
    """Fresh mutable source + call arguments (built outside the timed region)."""
    if c["source"] == "pop":
        func = list(c["data"]).pop
    elif c["source"] == "popleft":
        func = deque(c["data"]).popleft
    else:
        it = iter(c["data"])
        func = it.__next__
    first = None if c["first"] is None else (lambda v=c["first"]: v)
    return func, EXC[c["exc"]](RAISES[c["source"]]), first

def run(func, exc, first):
    try:
        return list(iter_except(func, exc, first))
    except Exception as e:
        return type(e).__name__

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for c in cases:
            h.update(repr(run(*setup(c))).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    rounds = [[setup(c) for c in cases] for _ in range(repeat)]
    acc = 0
    t0 = time.perf_counter()
    for args_list in rounds:
        for args in args_list:
            acc += len(run(*args))
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))

if __name__ == "__main__":
    main()
