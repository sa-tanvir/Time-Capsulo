#!/usr/bin/env python3
"""Download the pinned 2017-2019 repository snapshots listed in repos.csv and verify them.

Usage: python3 harness/fetch_repos.py [python] [go] [javascript] [rust] [java] [cpp]   (stdlib only; needs internet)
Each repo is fetched from GitHub as the tarball of its release tag, extracted to its `local_path`,
and checked against `tree_sha256` (sha256 over sorted relative paths + file contents)."""
import csv, hashlib, io, os, shutil, sys, tarfile, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tree_digest(root):
    h = hashlib.sha256()
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if d != "__pycache__")  # interpreter caches are not part of the source
        for f in sorted(fn):
            p = os.path.join(dp, f)
            if os.path.islink(p):
                continue
            h.update(os.path.relpath(p, root).encode() + b"\0" + open(p, "rb").read() + b"\0")
    return h.hexdigest()


def main():
    ok = True
    langs = set(sys.argv[1:])  # optional language filter, e.g. `fetch_repos.py go`
    for r in csv.DictReader(open(os.path.join(ROOT, "repos.csv"))):
        if langs and r["language"] not in langs:
            continue
        dest = os.path.join(ROOT, r["local_path"])
        if os.path.isdir(dest) and tree_digest(dest) == r["tree_sha256"]:
            print(f"ok      {r['name']} {r['tag']} (already present)")
            continue
        url = f"https://codeload.github.com/{r['github_repo']}/tar.gz/refs/tags/{r['tag']}"
        print(f"fetch   {r['name']} {r['tag']} <- {url}")
        data = urllib.request.urlopen(url, timeout=300).read()
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        os.makedirs(dest)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
            for m in tf.getmembers():
                parts = m.name.split("/", 1)
                if len(parts) < 2 or not parts[1] or ".." in parts[1].split("/"):
                    continue
                m.name = parts[1]
                tf.extract(m, dest)
        got = tree_digest(dest)
        if got != r["tree_sha256"]:
            ok = False
            print(f"MISMATCH {r['name']}: tree_sha256 {got} != {r['tree_sha256']}")
        else:
            print(f"ok      {r['name']} verified")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
