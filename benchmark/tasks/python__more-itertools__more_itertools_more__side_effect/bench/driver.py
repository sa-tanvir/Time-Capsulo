"""Bench driver for side_effect(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from more_itertools.more import side_effect

def source(data, fail_at):
    for i, x in enumerate(data):
        if i == fail_at:
            raise RuntimeError("boom")
        yield x

def run(c, log):
    """log records the interleaving of callbacks and yielded items."""
    func = (lambda x: log.append(("f", x))) if c["chunk"] is None else (lambda ch: log.append(("f", sum(ch), len(ch))))
    before = (lambda: log.append("B")) if c["before"] else None
    after = (lambda: log.append("A")) if c["after"] else None
    try:
        for x in side_effect(func, source(c["data"], c["fail_at"]), c["chunk"], before, after):
            log.append(x)
    except RuntimeError:
        log.append("E")
    return log

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for c in cases:
            h.update(repr(run(c, [])).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for c in cases:
            acc += len(run(c, []))
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))

if __name__ == "__main__":
    main()
