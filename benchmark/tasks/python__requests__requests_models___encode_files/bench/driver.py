"""Bench driver for RequestEncodingMixin._encode_files(). argv: <size> <repeat> <mode: check|time>"""
import hashlib, io, json, re, sys, time
from collections import OrderedDict
from requests.models import RequestEncodingMixin

enc = RequestEncodingMixin._encode_files


def blob(n, seed):
    return bytes((seed + i * 131 + (i >> 3)) % 256 for i in range(n))


class Unnamed(io.BytesIO):
    pass


def sc(x):
    if x is None:
        return None
    if "s" in x:
        return x["s"]
    if "b" in x:
        return x["b"].encode("utf-8")
    if "i" in x:
        return x["i"]
    return [sc(e) for e in x["list"]]


class Spec:
    """Pre-decoded case; build() makes fresh inputs (streams are consumed by the call)."""

    def __init__(self, c):
        self.c = c
        if "err" in c:
            return
        self.blobs = {}
        for _, fe in c["files"]:
            f = fe["f"]
            self.blobs[id(f)] = blob(f["len"], f["seed"])

    def fobj(self, f):
        b = self.blobs[id(f)]
        k = f["kind"]
        if k == "bytes":
            return b
        if k == "str":
            return b.decode("latin-1")
        if k == "bytearray":
            return bytearray(b)
        if k == "stream":
            return Unnamed(b)
        if k == "named_stream":
            s = io.BytesIO(b)
            s.name = "/some/dir/" + f["name"]
            return s
        if k == "int":
            return f["len"]
        return None

    def build(self):
        c = self.c
        if "err" in c:
            return ({"a": b"x"}, "a=b") if c["err"] == "strdata" else ({}, {"a": "b"})
        data = [(sc(k), sc(v)) for k, v in c["data"]]
        files = []
        for name, fe in c["files"]:
            fo = self.fobj(fe["f"])
            if fe["shape"] == 1:
                files.append((name, fo))
            else:
                t = (fe["fn"], fo, fe["ct"], fe["hdr"])[:fe["shape"]]
                files.append((name, t if fe["shape"] != 3 else list(t)))
        if c["data_kind"] == "dict":
            data = OrderedDict(data)
        elif c["data_kind"] == "none":
            data = None
        if c["files_kind"] == "dict":
            files = OrderedDict(files)
        return files, data


def normalise(res):
    body, ctype = res
    m = re.search(r"boundary=(\S+)", ctype)
    bnd = m.group(1)
    return body.replace(bnd.encode("ascii"), b"BOUNDARY"), ctype.replace(bnd, "BOUNDARY")


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json", encoding="utf-8") as fh:
        specs = [Spec(c) for c in json.load(fh)]
    if mode == "check":
        h = hashlib.sha256()
        for s in specs:
            files, data = s.build()
            try:
                body, ct = normalise(enc(files, data))
                h.update(b"ok:" + ct.encode() + b"\n" + body + b"\n")
            except Exception as e:
                h.update(("err:" + type(e).__name__ + ":" + repr(e.args) + "\n").encode())
        print(json.dumps({"cases": len(specs), "output_digest": h.hexdigest()}))
        return
    keep = 0
    elapsed = 0.0
    for _ in range(repeat):
        inputs = [s.build() for s in specs]      # untimed: fresh streams each repeat
        t0 = time.perf_counter()
        for files, data in inputs:
            try:
                keep += len(enc(files, data)[0])
            except ValueError:
                keep += 1
        elapsed += time.perf_counter() - t0
    print(keep, file=sys.stderr)
    print(json.dumps({"cases": len(specs), "repeat": repeat, "elapsed_s": elapsed}))


if __name__ == "__main__":
    main()
