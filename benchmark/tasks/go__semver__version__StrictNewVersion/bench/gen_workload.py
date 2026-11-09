"""Seeded workload generator for semver StrictNewVersion. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# size: (strings, max identifiers per pre-release / metadata, inner repetitions per pass)
SIZES = {"S": (20_000, 2, 2), "M": (20_000, 10, 1), "L": (4_000, 70, 1)}
WORDS = ["alpha", "beta", "rc", "pre", "dev", "SNAPSHOT", "build", "sha", "x", "Y", "rc1-with-hypen", "-1"]
EDGE = [
    "1.2.3", "1.2.3-alpha.01", "1.2.3+test.01", "1.2.3-alpha.-1", "v1.2.3", "1.0", "v1.0", "1", "v1",
    "1.2.beta", "v1.2.beta", "foo", "1.2-5", "v1.2-5", "1.2-beta.5", "v1.2-beta.5", "\n1.2", "\nv1.2",
    "1.2.0-x.Y.0+metadata", "v1.2.0-x.Y.0+metadata", "1.2.0-x.Y.0+metadata-width-hypen",
    "v1.2.0-x.Y.0+metadata-width-hypen", "1.2.3-rc1-with-hypen", "v1.2.3-rc1-with-hypen", "1.2.3.4",
    "v1.2.3.4", "1.2.2147483648", "1.2147483648.3", "2147483648.3.0", "", "0.0.0", "01.2.3", "1.02.3",
    "1.2.03", "1.2.3-0", "1.2.3-00", "1.2.3-0a", "1.2.3-a_b", "1.2.3+a_b", "1.2.3-a+b_c", "1.2.3-a_b+c_d",
    "1.2.3-alpha.01+meta", "1.2.3+meta+more", "1.2.3+b-c", "1.2.3-a-b-c", "a.01.3", "01.a.3", "1.2.3 ",
    " 1.2.3", "1.2.3-é", "18446744073709551615.18446744073709551615.18446744073709551615", "1.2.3-",
    "1.2.3+", "1.2.3-a..b", "1.2.3+a..b",
]

def ident(rng):
    r = rng.random()
    if r < 0.35:
        return str(rng.choice([0, rng.randint(1, 9), rng.randint(10, 999), rng.randint(1000, 10**12)]))
    if r < 0.75:
        return rng.choice(WORDS)
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
    return rng.choice("abcdefghijklmnopqrstuvwxyz") + "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 10)))

def num(rng):
    return str(rng.choice([0, 1, 2, rng.randint(0, 30), rng.randint(0, 10**9), rng.randint(0, 2**64 - 1)]))

def valid(rng, kmax):
    lo = 1 if kmax <= 2 else kmax // 3
    pre = [ident(rng) for _ in range(rng.randint(lo, kmax))] if rng.random() < 0.6 else []
    meta = [ident(rng) for _ in range(rng.randint(lo, kmax))] if rng.random() < 0.4 else []
    return [num(rng), num(rng), num(rng)], pre, meta

def render(core, pre, meta):
    return ".".join(core) + ("-" + ".".join(pre) if pre else "") + ("+" + ".".join(meta) if meta else "")

def corrupt(rng, core, pre, meta):
    r = rng.random()
    if r < 0.12:
        return "v" + render(core, pre, meta)                       # leading v
    if r < 0.24:
        return render(core[:rng.randint(1, 2)], pre, meta)           # missing components
    if r < 0.36:
        core[rng.randrange(3)] = "0" + str(rng.randint(1, 99))       # leading zero
        return render(core, pre, meta)
    if r < 0.48:
        i = rng.randrange(3)
        core[i] = core[i] + rng.choice(["a", "x", "_", " "])         # bad character in core
        return render(core, pre, meta)
    if r < 0.6:
        return render(core, pre, meta) + "." + str(rng.randint(0, 9)) if not (pre or meta) else render(core + ["4"], pre, meta)
    if r < 0.72 and pre:
        pre[rng.randrange(len(pre))] = "0" + str(rng.randint(0, 99))  # numeric pre-release with leading zero
        return render(core, pre, meta)
    if r < 0.86:
        pre = pre or [ident(rng)]
        pre[rng.randrange(len(pre))] += rng.choice(["_", "!", "~", "#"])
        return render(core, pre, meta)
    meta = meta or [ident(rng)]
    meta[rng.randrange(len(meta))] += rng.choice(["_", "!", "~", "#"])
    return render(core, pre, meta)

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, kmax, inner)) in enumerate(SIZES.items()):
        rng = random.Random(20191213 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            c, p, m = valid(rng, kmax)
            cases.append(render(c, p, m) if rng.random() < 0.75 else corrupt(rng, c, p, m))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"inner": inner, "cases": cases}))
