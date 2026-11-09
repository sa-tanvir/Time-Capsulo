"""Bench driver for SortedKeyList._check. argv: <size> <repeat> <mode: check|time>"""
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
import io


def corrupt(sl, kind, where):
    """Break exactly one invariant (all values are ints, so every comparison stays valid)."""
    nl = len(sl._lists)
    i = min(nl - 1, int(where * nl))
    keyed = hasattr(sl, "_keys")
    if kind == "len":
        sl._len += 1
    elif kind == "load":
        sl._load = 3
    elif kind == "maxes":
        sl._maxes[i] += 1
    elif kind == "maxes_len":
        sl._maxes.append(sl._maxes[-1])
    elif kind == "swap":
        order = sl._keys if keyed else sl._lists
        for j in list(range(i, nl)) + list(range(i)):
            sub = order[j]
            k = next((k for k in range(len(sub) - 1) if sub[k] < sub[k + 1]), None)
            if k is not None:
                sub[k], sub[k + 1] = sub[k + 1], sub[k]
                if keyed:
                    sl._lists[j][k], sl._lists[j][k + 1] = sl._lists[j][k + 1], sl._lists[j][k]
                return
        sl._len -= 1
    elif kind == "shrink_load":
        sl._load = 4
        if max(len(s) for s in sl._lists) <= 8:
            sl._len += 2
    elif kind == "index_root":
        sl._index[0] += 1
    elif kind == "index_leaf":
        sl._index[sl._offset + i] += 1
    elif kind == "index_inner":
        if sl._offset:
            sl._index[max(1, min(sl._offset - 1, int(where * sl._offset)))] += 1
        else:
            sl._index[0] -= 1
    elif kind == "key":
        sl._keys[i][-1] = sl._keys[i][-1] + 1 if sl._keys[i][-1] < sl._maxes[i] + 1 else 0
        sl._maxes[i] = sl._keys[i][-1]
    else:
        raise ValueError(kind)


def prepare(c):
    sl = build(c)
    if c["corrupt"]:
        if c["prebuild"] and not sl._index:
            sl._build_index()
        corrupt(sl, c["corrupt"], c["where"])
    return sl


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    cases = [prepare(c) for c in load(size)]
    real_stdout, sink = sys.stdout, io.StringIO()
    if mode == "check":
        h = hashlib.sha256()
        sys.stdout = sink
        try:
            for sl in cases:
                try:
                    out = repr(sl._check())
                except AssertionError:
                    out = "AssertionError"
                h.update(out.encode() + b"\n")
                h.update(repr((sl._len, sl._load, sl._offset, sl._index, sl._maxes, sl._lists,
                               getattr(sl, "_keys", None))).encode())
        finally:
            sys.stdout = real_stdout
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    sys.stdout = sink
    t0 = time.perf_counter()
    try:
        for _ in range(repeat):
            for sl in cases:
                try:
                    sl._check()
                    acc += 1
                except AssertionError:
                    acc += 2
                sink.seek(0)
                sink.truncate()
    finally:
        el = time.perf_counter() - t0
        sys.stdout = real_stdout
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
