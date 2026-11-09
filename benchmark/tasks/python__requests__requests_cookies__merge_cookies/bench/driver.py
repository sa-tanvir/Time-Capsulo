"""Bench driver for merge_cookies(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
from http import cookiejar as cookielib
from requests.cookies import RequestsCookieJar, create_cookie, merge_cookies


def jar_of(kind, items):
    if kind == "notajar":
        return {n: v for n, v, _, _ in items}
    jar = RequestsCookieJar() if kind == "requests" else cookielib.CookieJar()
    for name, value, domain, path in items:
        jar.set_cookie(create_cookie(name, value, domain=domain, path=path))
    return jar


def build(c):
    target = jar_of(c["target_kind"], c["target"])
    k = c["src_kind"]
    if k == "none":
        src = None
    elif k == "dict":
        src = {n: v for n, v, _, _ in c["src"]}
    else:
        src = jar_of(k, c["src"])
    return target, src


def snapshot(jar):
    return [(type(jar).__name__,)] + sorted(
        (ck.domain, ck.path, ck.name, ck.value, ck.secure, ck.expires) for ck in jar)


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        raw = json.load(fh)
    if mode == "check":
        h = hashlib.sha256()
        for c in raw:
            target, src = build(c)
            try:
                res = merge_cookies(target, src)
                out = "ok:" + repr(res is target) + repr(snapshot(res))
            except Exception as e:
                out = "err:" + type(e).__name__ + ":" + repr(e.args)
            h.update(out.encode() + b"\n")
        print(json.dumps({"cases": len(raw), "output_digest": h.hexdigest()}))
        return
    keep = 0
    elapsed = 0.0
    for _ in range(repeat):
        inputs = [build(c) for c in raw]          # untimed: target jars are mutated
        t0 = time.perf_counter()
        for target, src in inputs:
            try:
                keep += len(merge_cookies(target, src)._cookies)
            except ValueError:
                keep += 1
        elapsed += time.perf_counter() - t0
    print(keep, file=sys.stderr)
    print(json.dumps({"cases": len(raw), "repeat": repeat, "elapsed_s": elapsed}))


if __name__ == "__main__":
    main()
