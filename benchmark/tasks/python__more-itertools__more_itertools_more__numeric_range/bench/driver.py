"""Bench driver for numeric_range(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from more_itertools.more import numeric_range

EPOCH = datetime(2000, 1, 1)

def dec(a):
    t, v = a
    if t == "int":
        return int(v)
    if t == "float":
        return float(v)
    if t == "frac":
        return Fraction(v[0], v[1])
    if t == "dec":
        return Decimal(v)
    if t == "dt":
        return EPOCH + timedelta(seconds=v)
    return timedelta(seconds=v)

def canon(x):
    # type + exact value; Decimal normalised so equal values with different exponents agree
    if isinstance(x, Decimal):
        return ("Decimal", str(x.normalize()))
    if isinstance(x, float):
        return ("float", x.hex())
    return (type(x).__name__, repr(x))

def call(args):
    try:
        return [canon(v) for v in numeric_range(*args)]
    except (TypeError, ValueError) as e:
        return type(e).__name__

def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [[dec(a) for a in c] for c in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for args in cases:
            h.update(repr(call(args)).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for args in cases:
            try:
                acc += len(list(numeric_range(*args)))
            except ValueError:
                acc += 1
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))

if __name__ == "__main__":
    main()
