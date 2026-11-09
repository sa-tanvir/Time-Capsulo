"""Bench driver for cookiejar_from_dict(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from http import cookiejar as cookielib
from requests.cookies import RequestsCookieJar, create_cookie, cookiejar_from_dict


def build(c):
    jar = None
    if c["jar_kind"] != "none":
        jar = RequestsCookieJar() if c["jar_kind"] == "requests" else cookielib.CookieJar()
        for name, value, domain, path in c["jar"]:
            jar.set_cookie(create_cookie(name, value, domain=domain, path=path))
    return c["dict"], jar, c["overwrite"]


def call(d, jar, ow):
    if ow is None:
        return cookiejar_from_dict(d, jar)
    return cookiejar_from_dict(d, jar, ow)


def snapshot(jar):
    return [(type(jar).__name__,)] + sorted(
        (ck.domain, ck.path, ck.name, ck.value, ck.secure, ck.expires, ck.discard) for ck in jar)


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        raw = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for c in raw:
            d, jar, ow = build(c)
            res = call(d, jar, ow)
            same = jar is None or res is jar
            h.update((repr(same) + repr(snapshot(res)) + "\n").encode())
        print(json.dumps({"cases": len(raw), "output_digest": h.hexdigest()}))
        return
    keep = 0
    elapsed = 0.0
    for _ in range(repeat):
        inputs = [build(c) for c in raw]          # untimed: jars are mutated by the call
        t0 = time.perf_counter()
        for d, jar, ow in inputs:
            keep += len(call(d, jar, ow)._cookies)
        elapsed += time.perf_counter() - t0
    print(keep, file=sys.stderr)
    print(json.dumps({"cases": len(raw), "repeat": repeat, "elapsed_s": elapsed}))


if __name__ == "__main__":
    main()
