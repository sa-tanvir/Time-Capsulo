"""Bench driver for click._bashcomplete.is_incomplete_option. argv: <size> <repeat> <mode: check|time>"""
import hashlib, json, sys, time
import click
from click._bashcomplete import is_incomplete_option


def build(p):
    if p["kind"] == "arg":
        return click.Argument(p["decls"], nargs=p["nargs"], required=False)
    if p["kind"] == "flag":
        return click.Option(p["decls"], is_flag=True)
    if p["kind"] == "count":
        return click.Option(p["decls"], count=True)
    if p["kind"] == "boolpair":
        return click.Option(p["decls"])
    return click.Option(p["decls"], nargs=p["nargs"])


def main():
    size, repeat, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(f"/task/bench/workload_{size}.json") as fh:
        data = json.load(fh)
    ps = [build(p) for p in data["params"]]
    cases = [(q[1], ps[q[0]]) for q in data["queries"]] * data["passes"]
    if mode == "check":
        h = hashlib.sha256()
        for args, p in cases:
            h.update(b"1" if is_incomplete_option(args, p) else b"0")
        print(json.dumps({"cases": len(cases), "output_digest": h.hexdigest()}))
        return
    acc = 0
    t0 = time.perf_counter()
    for _ in range(repeat):
        for args, p in cases:
            if is_incomplete_option(args, p):
                acc += 1
    el = time.perf_counter() - t0
    print(acc, file=sys.stderr)
    print(json.dumps({"cases": len(cases), "repeat": repeat, "elapsed_s": el}))


if __name__ == "__main__":
    main()
