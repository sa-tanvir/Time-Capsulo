"""Seeded workload generator for doc.hasSeeAlso. Usage: python3 gen_workload.py <out_dir>"""
import json, random, sys
from pathlib import Path

# (cases, children per root, depth of each child's non-runnable chain)
SIZES = {"S": (3000, 3, 1), "M": (300, 30, 4), "L": (30, 300, 12)}

def chain(rng, uid, depth):
    """A child whose availability is only decided at the bottom of a chain of non-runnable commands."""
    leaf = {"u": "leaf%d" % uid, "r": True}
    r = rng.random()
    if r < 0.6:
        leaf["h"] = True          # hidden leaf -> whole chain unavailable
    elif r < 0.9:
        leaf["d"] = "old"         # deprecated leaf -> unavailable
    node = leaf
    for k in range(depth):
        node = {"u": "mid%d_%d" % (uid, k), "c": [node]}
    return node

def case(rng, width, depth):
    kids = []
    for j in range(rng.randint(0, width)):
        r = rng.random()
        if r < 0.3:
            kids.append({"u": "hid%d" % j, "r": True, "h": True})
        elif r < 0.5:
            kids.append({"u": "dep%d" % j, "r": True, "d": "gone"})
        elif r < 0.6:
            kids.append({"u": "topic%d" % j})
        else:
            kids.append(chain(rng, j, depth))
    if rng.random() < 0.15:
        kids.append({"u": "zz%d" % rng.randrange(1000), "r": True})
    root = {"u": "root", "r": True, "c": kids}
    path = []
    if kids and rng.random() < 0.15:
        path = [rng.randrange(len(kids))]
    return {"t": root, "p": path, "ih": rng.random() < 0.3}

EDGE = [{"t": {"u": "root", "r": True}, "p": [], "ih": False},
        {"t": {"u": "root", "r": True, "c": [{"u": "sub"}]}, "p": [0], "ih": False},
        {"t": {"u": "root", "c": [{"u": "aaa", "r": True, "h": True}, {"u": "bbb", "r": True}]}, "p": [], "ih": False},
        {"t": {"u": "root", "c": [{"u": "aaa", "r": True, "h": True}, {"u": "ccc", "r": True, "d": "x"}]}, "p": [], "ih": False},
        {"t": {"u": "root", "r": True, "c": [{"u": "x", "r": True, "h": True}]}, "p": [], "ih": True},
        {"t": {"u": "root", "c": [{"u": "topic"}]}, "p": [], "ih": False},
        {"t": {"u": "root", "c": [{"u": "grp", "c": [{"u": "leaf", "r": True}]}]}, "p": [], "ih": False}]

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, (size, (n, width, depth)) in enumerate(SIZES.items()):
        rng = random.Random(20190607 + i)
        cases = list(EDGE) if size == "S" else []
        while len(cases) < n:
            cases.append(case(rng, width, depth))
        (out_dir / f"workload_{size}.json").write_text(json.dumps({"cases": cases}))
