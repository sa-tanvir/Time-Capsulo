"""Bench driver for parse_header_links(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from requests.utils import parse_header_links


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for v in cases:
            try:
                out = "ok:" + repr([list(d.items()) for d in parse_header_links(v)])
            except Exception as e:
                out = "err:" + type(e).__name__
            h.update(out.encode() + b"\n")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    keep = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for v in cases:
            keep += len(parse_header_links(v))
    el = time.perf_counter() - t0
    print(keep, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
