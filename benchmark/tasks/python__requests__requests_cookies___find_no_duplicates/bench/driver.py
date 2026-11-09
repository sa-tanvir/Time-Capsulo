"""Bench driver for RequestsCookieJar._find_no_duplicates(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from requests.cookies import RequestsCookieJar, create_cookie


def build(c):
    jar = RequestsCookieJar()
    for name, value, domain, path in c["cookies"]:
        jar.set_cookie(create_cookie(name, value, domain=domain, path=path))
    return jar, [tuple(q) for q in c["queries"]]


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        cases = [build(c) for c in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for jar, qs in cases:
            for name, domain, path in qs:
                try:
                    out = "ok:" + repr(jar._find_no_duplicates(name, domain, path))
                except Exception as e:
                    out = "err:" + type(e).__name__ + ":" + repr(e.args)
                h.update(out.encode() + b"\n")
            h.update(repr(sorted((c.name, c.value, c.domain, c.path) for c in jar)).encode())
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    keep = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for jar, qs in cases:
            for name, domain, path in qs:
                try:
                    keep += len(jar._find_no_duplicates(name, domain, path))
                except (KeyError, RuntimeError):
                    keep += 1
    el = time.perf_counter() - t0
    print(keep, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
