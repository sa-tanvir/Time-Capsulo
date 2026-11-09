"""Bench driver for SortedKeyList.count. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, random, sys, time
from operator import neg
from sortedcontainers import SortedList, SortedKeyList


def div3(v):
    return v // 3


def mod101(v):
    return v % 101


KEYS = {"neg": neg, "div3": div3, "mod101": mod101}


def build(r):
    """Expand a container recipe (seeded values, load factor, key, optional pre-built index)."""
    rng = random.Random(r["seed"])
    vals = [rng.randrange(r["vmax"]) for _ in range(r["n"])]
    sl = SortedKeyList(vals, key=KEYS[r["key"]]) if r["key"] else SortedList(vals)
    sl._reset(r["load"])
    if r["prebuild"] and sl._lists:
        sl._build_index()
    return sl


def load(size):
    with open(f"/task/bench/workload_{size}.json") as fh:
        return json.load(fh)


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    cases = [(build(c), c["queries"]) for c in load(size)]
    n_calls = sum(len(q) for _, q in cases)
    if mode == "check":
        h = hashlib.sha256()
        for sl, qs in cases:
            h.update(repr([sl.count(v) for v in qs]).encode())
            h.update(repr(list(sl)).encode())
        print(json.dumps({"cases": n_calls, "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for sl, qs in cases:
            count = sl.count
            for v in qs:
                acc += count(v)
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": n_calls, "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
