"""Bench driver for _timelex.get_token. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from dateutil.parser._parser import _timelex


def tokens(lex):
    out = []
    get = lex.get_token
    tok = get()
    while tok is not None:
        out.append(tok)
        tok = get()
    return out


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for s in cases:
            lex = _timelex(s)
            toks = tokens(lex)
            h.update((repr(toks) + repr(lex.get_token()) + "\n").encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    el, acc = 0.0, 0
    for _ in range(repeat):
        lexers = [_timelex(s) for s in cases]   # fresh (mutable) lexers, built outside the timed region
        t0 = time.perf_counter()
        for lex in lexers:
            acc += len(tokens(lex))
        el += time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
