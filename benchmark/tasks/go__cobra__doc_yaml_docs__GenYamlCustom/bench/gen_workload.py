"""Seeded workload generator for doc.GenYamlCustom. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# ---- command-tree generator (shared by the cobra Time Capsulo workloads) ----
SHORTS = "abcdefgijklmnopqrstuwxyzABCDEFGIJKLMNOPQRSTUWXYZ"  # no h / v / H / V
WORDS = ["get", "set", "list", "apply", "delete", "describe", "logs", "exec", "run", "config",
         "create", "edit", "patch", "scale", "rollout", "top", "proxy", "auth", "plugin", "cp"]
TEXT = ["Print", "the", "client", "and", "server", "version", "information", "for", "the", "current",
        "context", "with", "'quotes'", "\"dq\"", "été", "--flag", "a:b", "#", "*", "-"]

def sentence(rng, lo, hi):
    return " ".join(rng.choice(TEXT) for _ in range(rng.randint(lo, hi)))

class TreeGen:
    def __init__(self, rng, flag_kinds=("string", "bool", "int", "slice"), annotations=None):
        self.rng, self.uid, self.kinds = rng, 0, flag_kinds
        self.annotations = annotations or []
        self.shorts = []

    def flag(self, persistent):
        rng = self.rng
        self.uid += 1
        kind = rng.choice(self.kinds)
        name = "%s-%d" % (rng.choice(WORDS), self.uid)
        short = self.shorts.pop() if self.shorts and rng.random() < 0.5 else ""
        default = {"string": rng.choice(["", "x", "two words", "über"]),
                   "bool": rng.choice(["true", "false"]),
                   "int": str(rng.randint(-5, 500)),
                   "slice": rng.choice(["", "a", "a,b,c"])}[kind]
        f = [kind, name, short, default, sentence(rng, 0, 8), "p" if persistent else "l",
             "hidden" if rng.random() < 0.1 else "", "use other" if rng.random() < 0.08 else ""]
        if self.annotations and rng.random() < 0.3:
            key, vals = rng.choice(self.annotations)
            f += [key] + list(vals)
        return f

    def node(self, depth, max_children, max_flags, is_root=False):
        rng = self.rng
        if is_root:
            self.shorts = list(SHORTS)
            rng.shuffle(self.shorts)
        self.uid += 1
        n = {"u": "%s%d" % (rng.choice(WORDS), self.uid) + (" [flags] ARG" if rng.random() < 0.3 else ""),
             "s": sentence(rng, 0, 6), "l": sentence(rng, 0, 30), "r": rng.random() < 0.8}
        if rng.random() < 0.3:
            n["e"] = sentence(rng, 2, 10) + "\n" + sentence(rng, 2, 10)
        if not is_root and rng.random() < 0.1:
            n["h"] = True
        if not is_root and rng.random() < 0.08:
            n["d"] = "use something else"
        if rng.random() < 0.3:
            n["a"] = [rng.choice(WORDS) + str(self.uid) + chr(97 + i) for i in range(rng.randint(1, 3))]
        if rng.random() < 0.3:
            n["va"] = [rng.choice(WORDS) for _ in range(rng.randint(1, 4))]
        if rng.random() < 0.2:
            n["aa"] = [rng.choice(WORDS) + "s" for _ in range(rng.randint(1, 3))]
        if rng.random() < 0.1:
            n["nt"] = True
        n["f"] = [self.flag(rng.random() < 0.3) for _ in range(rng.randint(0, max_flags))]
        if depth > 0:
            n["c"] = [self.node(depth - 1, max_children, max_flags) for _ in range(rng.randint(0, max_children))]
        return n

def spine_case(rng, width, nflags, anc_flags, child_flags=2):
    """Root -> 0..2 intermediate commands -> target; the target has `width` children and up to
    `nflags` flags, ancestors carry up to `anc_flags` (often persistent) flags."""
    g = TreeGen(rng)
    root = g.node(0, 0, anc_flags, is_root=True)
    cur = root
    for _ in range(rng.randint(0, 2)):
        nxt = g.node(0, 0, anc_flags)
        nxt.pop("h", None); nxt.pop("d", None); nxt["r"] = True
        cur.setdefault("c", []).append(nxt)
        for _ in range(rng.randint(0, 3)):
            cur["c"].append(g.node(0, 0, 1))
        cur = nxt
    tgt = g.node(0, 0, nflags) if cur is not root else root
    if tgt is not root:
        tgt.pop("h", None); tgt.pop("d", None)
        cur.setdefault("c", []).append(tgt)
    tgt["c"] = [g.node(0, 0, child_flags) for _ in range(rng.randint(0, width))]
    if tgt is root:
        root["f"] += [g.flag(rng.random() < 0.3) for _ in range(rng.randint(0, nflags))]
    tgt["tgt"] = True
    sort_tree(root)
    return root, find_path(root)

def sort_tree(n):
    kids = n.get("c", [])
    for k in kids:
        sort_tree(k)
    kids.sort(key=lambda k: k["u"].split(" ")[0])

def find_path(n):
    if n.get("tgt"):
        return []
    for i, k in enumerate(n.get("c", [])):
        p = find_path(k)
        if p is not None:
            return [i] + p
    return None


# (cases, max children of the target, max flags of the target, max flags per ancestor)
SIZES = {"S": (300, 3, 3, 2), "M": (40, 30, 30, 10), "L": (6, 300, 300, 40)}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, width, nflags, anc)) in enumerate(SIZES.items()):
        rng = random.Random(20190607 + i)
        cases = []
        while len(cases) < n:
            root, path = spine_case(rng, width, nflags, anc)
            cases.append({"t": root, "p": path})
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
