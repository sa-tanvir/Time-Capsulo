"""Bench driver for unquote_unreserved(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from requests.utils import unquote_unreserved
from requests.exceptions import InvalidURL


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json", encoding="utf-8") as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for v in cases:
            try:
                out = "ok:" + unquote_unreserved(v)
            except Exception as e:
                out = "err:" + type(e).__name__ + ":" + repr(e.args)
            h.update(out.encode("utf-8") + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    keep = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for v in cases:
            try:
                keep += len(unquote_unreserved(v))
            except InvalidURL:
                keep += 1
    el = time.perf_counter() - t0
    print(keep, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
