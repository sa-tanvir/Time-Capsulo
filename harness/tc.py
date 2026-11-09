#!/usr/bin/env python3
"""Time Capsulo benchmark harness.

Commands
  setup      <repo_key>                    working copy + test-only dependencies (run once per repo)
  baseline   <repo_key>                    run the repo's own test suite twice on pristine code
  candidates <repo_key> [--max N] [--until K]   static filter + sabotage coverage (stop after K selectable)
  make-task  <repo_key> <candidate_id>     scaffold benchmark/tasks/<task_id>/ from a candidate
  eval       <task_id> <impl_file>         inject an implementation, run tests + differential check
  bench      <task_id> <impl_file> [--size S|M|L] [--repeat R] [--min-time 1.0]   time the bench driver
  expect     <task_id>                     record reference output digests for each workload size
  check      <task_id> | --all [--repo K]  validate a task end to end (reference passes, stub fails, ...)
  select     <repo_key> [--k 10]           deterministic choice of tasks from eligible candidates
  summary                                  write benchmark/tasks.csv and per-language counts
  prompt     <task_id> [--write]           the exact prompt given to the model (--write saves prompt.md)
  run        <task_id> <impl|reply> [--label L] [--out f.jsonl]   GATED PIPELINE: interface check -> tests
             -> output checks (S,M,L) -> only if correct: calibrated timing + peak memory per size.
             Use impl=reference for the human baseline. Status labels: passed, failed_tests, wrong_output,
             compile_error, timeout, crashed, interface_violation, format_violation, no_code

eval/bench accept either a code file or a raw model reply (the first ``` code block is used).

Repo configs live in benchmark/repos/<repo_key>.json, tasks in benchmark/tasks/<task_id>/.
All repo code runs inside Docker images (harness/docker/*.Dockerfile); the harness runs on the host.
"""
import argparse
import csv
import fcntl
import fnmatch
import hashlib
import json
import math
import os
import re
import shlex
import shutil
import subprocess
import sys
import textwrap
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import lizard

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "benchmark"
WORK = ROOT / ".work"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import langs  # noqa: E402


# ---------------------------------------------------------------- config / io

def repos_csv():
    with (ROOT / "repos.csv").open() as fh:
        return {f"{r['language']}__{r['name']}": r for r in csv.DictReader(fh)}


def load_repo(key):
    cfg = json.loads((BENCH / "repos" / f"{key}.json").read_text())
    meta = repos_csv()[key]
    cfg.setdefault("path", meta["local_path"])
    cfg.setdefault("language", meta["language"])
    cfg.update({"url": f"https://github.com/{meta['github_repo']}", "tag": meta["tag"],
                "commit_sha": meta["commit_sha"], "release_date": meta["release_date"]})
    cfg["key"] = key
    cfg["abs_path"] = ROOT / cfg["path"]
    return cfg


def load_task(task_id):
    d = BENCH / "tasks" / task_id
    t = json.loads((d / "task.json").read_text())
    t["dir"] = d
    return t


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n")


class RepoLock:
    def __init__(self, key):
        WORK.mkdir(exist_ok=True)
        self.f = open(WORK / f"{key}.lock", "w")

    def __enter__(self):
        fcntl.flock(self.f, fcntl.LOCK_EX)

    def __exit__(self, *a):
        fcntl.flock(self.f, fcntl.LOCK_UN)


def workspace(cfg):
    """Persistent working copy of a repo (keeps build artefacts between runs)."""
    ws = WORK / cfg["key"]
    if not ws.exists():
        shutil.copytree(cfg["abs_path"], ws, symlinks=True)
    return ws


# Files the harness has (re)written in a workspace, with their sha256. Docker Desktop on macOS can
# briefly show a container the *previous* content of a just-rewritten bind-mounted file, so every
# container run first waits until it sees exactly these contents (see docker_run).
_EXPECTED_FILES = {}


def note_written(cfg, rel):
    data = (workspace(cfg) / rel).read_bytes()
    _EXPECTED_FILES.setdefault(cfg["key"], {})[rel] = hashlib.sha256(data).hexdigest()


def restore_file(cfg, rel):
    # copyfile (not copy2): the restored file must get a *new* mtime, otherwise mtime-based
    # build tools (make, cargo, maven) may keep the artefacts compiled from the injected version
    shutil.copyfile(cfg["abs_path"] / rel, workspace(cfg) / rel)
    note_written(cfg, rel)


class StaleFileError(RuntimeError):
    pass


def freshness_guard(cfg):
    parts = []
    for rel, sha in _EXPECTED_FILES.get(cfg["key"], {}).items():
        q = shlex.quote("/w/" + rel)
        parts.append(
            f'for _i in $(seq 1 100); do [ "$(sha256sum {q} 2>/dev/null | cut -c1-64)" = "{sha}" ] && break; '
            f'ls -la "$(dirname {q})" >/dev/null 2>&1; sleep 0.1; done; '
            f'[ "$(sha256sum {q} | cut -c1-64)" = "{sha}" ] || {{ echo "TC_STALE_FILE {q}" >&2; exit 97; }}; ')
    return "".join(parts)


def fill(template, **kw):
    """Substitute {task} {size} {repeat} {mode} only, so literal braces (e.g. find -exec {}) survive."""
    for k, v in kw.items():
        template = template.replace("{" + k + "}", str(v))
    return template


# ---------------------------------------------------------------- docker

def docker_run(cfg, cmd, timeout=None, extra_mounts=()):
    ws = workspace(cfg)
    # fresh directory per run: re-creating the same bind-mounted path confuses Docker Desktop file sharing
    out = WORK / "out" / f"{cfg['key']}-{os.getpid()}-{time.time_ns()}"
    out.mkdir(parents=True)
    name = f"tc-{cfg['key'].replace('_', '-').replace('.', '-')}-{os.getpid()}-{time.time_ns()}"
    args = ["docker", "run", "--rm", "--name", name, "--network", cfg.get("network", "none"),
            "--memory", cfg.get("memory", "4g"),
            "-v", f"{ws}:/w", "-v", f"{out}:/out", "-w", "/w"]
    for vol, path in cfg.get("cache_volumes", {}).items():
        args += ["-v", f"{vol}:{path}"]
    args += ["-v", f"{ROOT / 'harness' / 'tools'}:/opt/tctools:ro"]
    for host, cont in extra_mounts:
        args += ["-v", f"{host}:{cont}"]
    for k, v in cfg.get("env", {}).items():
        args += ["-e", f"{k}={v}"]
    args += [cfg["image"], "bash", "-c", freshness_guard(cfg) + cmd]
    t0 = time.time()
    try:
        p = subprocess.run(args, capture_output=True, text=True,
                           timeout=timeout or cfg.get("timeout", 900))
        rc, log = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        subprocess.run(["docker", "kill", name], capture_output=True)
        tail = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        rc, log = -9, f"TIMEOUT after {e.timeout}s\n" + tail
    if rc == 97 and "TC_STALE_FILE" in log:
        raise StaleFileError(f"container never saw the written file contents: {log[-500:]}")
    return rc, log, out, time.time() - t0


# ---------------------------------------------------------------- test results

def parse_junit(out_dir):
    res = {}
    for xml in sorted(Path(out_dir).rglob("*.xml")):
        try:
            tree = ET.parse(xml)
        except ET.ParseError:
            continue
        for tc in tree.iter("testcase"):
            tid = f"{tc.get('classname', '')}::{tc.get('name', '')}"
            if tc.find("skipped") is not None:
                st = "skipped"
            elif tc.find("failure") is not None or tc.find("error") is not None:
                st = "failed"
            else:
                st = "passed"
            # a test id seen twice keeps the worst status
            if res.get(tid) != "failed":
                res[tid] = st
    return res


def parse_go_json(out_dir, log):
    res = {}
    src = Path(out_dir) / "go-test.json"
    lines = src.read_text().splitlines() if src.exists() else log.splitlines()
    for line in lines:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("Test") and ev.get("Action") in ("pass", "fail", "skip"):
            tid = f"{ev.get('Package', '')}::{ev['Test']}"
            res[tid] = {"pass": "passed", "fail": "failed", "skip": "skipped"}[ev["Action"]]
    return res


CARGO_RE = re.compile(r"^test (\S+) \.\.\. (ok|FAILED|ignored)", re.M)
TAP_RE = re.compile(r"^(not ok|ok)\s+\d+\s*-?\s*(.*?)(\s+#\s*(SKIP|TODO).*)?$", re.M)


def parse_results(cfg, out_dir, log):
    fmt = cfg["result_format"]
    if fmt == "junit":
        return parse_junit(out_dir)
    if fmt == "go-json":
        return parse_go_json(out_dir, log)
    if fmt == "cargo":
        res = {}
        # cargo prints "Running target/debug/deps/<bin>" before each binary's tests
        current = ""
        for line in log.splitlines():
            m = re.match(r"\s*Running (\S+)", line) or re.match(r"\s*Doc-tests (\S+)", line)
            if m:
                current = re.sub(r"-[0-9a-f]{16}$", "", Path(m.group(1)).name)
                continue
            m = CARGO_RE.match(line)
            if m:
                res[f"{current}::{m.group(1)}"] = {"ok": "passed", "FAILED": "failed", "ignored": "skipped"}[m.group(2)]
        return res
    if fmt == "tap":
        res, seen = {}, {}
        for m in TAP_RE.finditer(log):
            name = m.group(2).strip()
            seen[name] = seen.get(name, 0) + 1
            tid = f"{name}#{seen[name]}" if seen[name] > 1 else name
            res[tid] = "skipped" if m.group(4) else ("passed" if m.group(1) == "ok" else "failed")
        return res
    if fmt == "regex":
        # cfg["result_regex"] must have named groups `name` and `status`; cfg["pass_values"] list
        res = {}
        for m in re.finditer(cfg["result_regex"], log, re.M):
            res[m.group("name")] = "passed" if m.group("status") in cfg["pass_values"] else "failed"
        return res
    raise ValueError(f"unknown result_format {fmt}")


def run_tests(cfg, timeout=None, cmd=None):
    cmd = cmd or cfg["test_cmd"]
    if cfg.get("build_cmd"):
        cmd = f"( {cfg['build_cmd']} ) && ( {cmd} )"
    if timeout is None and (BENCH / "repos" / f"{cfg['key']}.baseline.json").exists():
        base_secs = max(load_baseline(cfg["key"])["secs"])
        timeout = int(cfg.get("timeout", max(180, 8 * base_secs + 60)))
    rc, log, out, secs = docker_run(cfg, cmd, timeout)
    res = parse_results(cfg, out, log)
    shutil.rmtree(out, ignore_errors=True)
    timed_out = rc == -9
    crashed = not res and rc in (134, 137, 139)  # abort / OOM-kill / segfault
    build_failed = not res and rc != 0 and not timed_out and not crashed
    return {"rc": rc, "tests": res, "build_failed": build_failed, "timed_out": timed_out, "crashed": crashed,
            "secs": round(secs, 1), "log_tail": log[-4000:]}


# ---------------------------------------------------------------- baseline

def cmd_baseline(a):
    cfg = load_repo(a.repo)
    with RepoLock(cfg["key"]):
        if cfg.get("setup_cmd"):
            rc, log, _, _ = docker_run(cfg, cfg["setup_cmd"], timeout=3600) if not cfg.get("setup_network") else \
                docker_run({**cfg, "network": "bridge"}, cfg["setup_cmd"], timeout=3600)
            if rc != 0:
                print(log[-3000:])
                sys.exit("setup_cmd failed")
        r1 = run_tests(cfg)
        r2 = run_tests(cfg)
    if r1["build_failed"]:
        print(r1["log_tail"])
        sys.exit("baseline build/test run failed (no parsable results)")
    stable = {t for t, s in r1["tests"].items() if s == "passed" and r2["tests"].get(t) == "passed"}
    flaky = sorted(t for t in set(r1["tests"]) | set(r2["tests"]) if r1["tests"].get(t) != r2["tests"].get(t))
    failing = sorted(t for t, s in r1["tests"].items() if s == "failed" and r2["tests"].get(t) == "failed")
    base = {"repo": cfg["key"], "n_tests": len(r1["tests"]), "passing": sorted(stable), "flaky": flaky,
            "failing_at_baseline": failing, "secs": [r1["secs"], r2["secs"]]}
    write_json(BENCH / "repos" / f"{cfg['key']}.baseline.json", base)
    print(f"{cfg['key']}: {len(r1['tests'])} tests, {len(stable)} stable-passing, {len(flaky)} flaky, "
          f"{len(failing)} failing at baseline, {r1['secs']}s per run")


def cmd_setup(a):
    """Create the repo's working copy and install its test-only dependencies (setup_cmd), without touching
    the published baseline."""
    cfg = load_repo(a.repo)
    with RepoLock(cfg["key"]):
        ws = workspace(cfg)
        lock = BENCH / "lockfiles" / f"{cfg['key']}.Cargo.lock"
        if lock.exists():  # exact dependency versions the baselines were made with (Cargo cannot resolve "as of a date")
            shutil.copyfile(lock, ws / "Cargo.lock")
        if cfg.get("setup_cmd"):
            run_cfg = {**cfg, "network": "bridge"} if cfg.get("setup_network") else cfg
            rc, log, out, _ = docker_run(run_cfg, cfg["setup_cmd"], timeout=3600)
            shutil.rmtree(out, ignore_errors=True)
            if rc != 0:
                print(log[-3000:])
                sys.exit(f"{cfg['key']}: setup_cmd failed")
    print(f"{cfg['key']}: ready")


def load_baseline(key):
    return json.loads((BENCH / "repos" / f"{key}.baseline.json").read_text())


# ---------------------------------------------------------------- candidates

def iter_functions(cfg):
    root = cfg["abs_path"]
    for pat in cfg["src_globs"]:
        for p in sorted(root.glob(pat)):
            rel = p.relative_to(root).as_posix()
            if any(fnmatch.fnmatch(rel, ex) for ex in cfg.get("exclude_globs", [])):
                continue
            info = lizard.analyze_file(str(p))
            for f in info.function_list:
                yield rel, f


def candidate_id(rel, f):
    return f"{rel}::{f.name}@{f.start_line}"


def cmd_candidates(a):
    cfg = load_repo(a.repo)
    lang = langs.get(cfg["language"])
    base = load_baseline(cfg["key"])
    passing = set(base["passing"])
    rows = []
    seen_names = {}
    for rel, f in iter_functions(cfg):
        src = (cfg["abs_path"] / rel).read_text(errors="replace").splitlines(keepends=True)
        ext = lang.extent(src, f.start_line, f.end_line, f.name)
        end = ext["end"] if ext else f.end_line
        body = "".join(src[f.start_line - 1:end])
        row = {"candidate_id": candidate_id(rel, f), "file": rel, "name": f.name, "long_name": f.long_name,
               "start": f.start_line, "end": end, "nloc": f.nloc, "ccn": f.cyclomatic_complexity,
               "params": len(f.parameters), "has_loop": lang.has_loop(body, f.name),
               "n_covering": "", "status": "", "reason": ""}
        seen_names[f.name] = seen_names.get(f.name, 0) + 1
        reasons = []
        if f.nloc < cfg.get("min_nloc", 8):
            reasons.append(f"nloc<{cfg.get('min_nloc', 8)}")
        if f.cyclomatic_complexity < cfg.get("min_ccn", 3):
            reasons.append(f"ccn<{cfg.get('min_ccn', 3)}")
        if not row["has_loop"]:
            reasons.append("no_loop_or_recursion")
        if f.nloc > cfg.get("max_nloc", 150):
            reasons.append(f"nloc>{cfg.get('max_nloc', 150)}")
        nd = lang.nondeterminism(body)
        if nd:
            reasons.append(f"nondeterministic:{nd}")
        if ext is None:
            reasons.append("extent_unparsable")
        row["status"] = "rejected_static" if reasons else "pending"
        row["reason"] = ";".join(reasons)
        rows.append(row)

    pend = [r for r in rows if r["status"] == "pending"]
    pend.sort(key=lambda r: -r["ccn"])
    if a.max:
        for r in pend[a.max:]:
            r["status"], r["reason"] = "not_sampled", f"beyond --max {a.max}"
        pend = pend[:a.max]
    print(f"{cfg['key']}: {len(rows)} functions, {len(pend)} pass static filters -> sabotage runs")
    good = 0
    with RepoLock(cfg["key"]):
        for i, r in enumerate(pend, 1):
            if a.until and good >= a.until:
                r["status"], r["reason"] = "not_sampled", f"stopped after {a.until} selectable candidates (--until)"
                continue
            res = sabotage(cfg, lang, r, passing)
            r.update(res)
            if r["status"] == "eligible" and int(r["n_covering"]) >= 2 and not (
                    cfg["language"] == "python" and "." in r["name"]) and "anonymous" not in r["name"].lower():
                good += 1
            print(f"  [{i}/{len(pend)}] {r['candidate_id']}: {r['status']} {r['reason']} covering={r['n_covering']}",
                  flush=True)
    out = BENCH / "logs" / "candidates" / f"{cfg['key']}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) + ["covering_tests"], extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {out.relative_to(ROOT)}")


def sabotage(cfg, lang, r, passing):
    rel = r["file"]
    ws = workspace(cfg)
    src = (cfg["abs_path"] / rel).read_text(errors="replace").splitlines(keepends=True)
    ext = lang.extent(src, r["start"], r["end"], r["name"])
    stub = lang.make_stub(src, ext)
    new = src[:ext["start"] - 1] + [stub + ext["suffix"]] + src[ext["end"]:]
    try:
        (ws / rel).write_text("".join(new))
        note_written(cfg, rel)
        # optional faster, targeted test command for the scan only (final checks always use test_cmd)
        scan = cfg.get("scan_test_cmd")
        scan = fill(scan, file=rel, stem=Path(rel).stem, name=r["name"].split("::")[-1].split(".")[-1]) if scan else None
        res = run_tests(cfg, cmd=scan)
        if res["build_failed"]:
            res = run_tests(cfg, cmd=scan)  # confirm before rejecting
    finally:
        restore_file(cfg, rel)
    if res["build_failed"]:
        return {"status": "rejected_sabotage", "reason": "stub_does_not_build", "n_covering": 0}
    if res["tests"] and scan:  # targeted scan: only tests that actually ran count
        covering = sorted(t for t in passing if t in res["tests"] and res["tests"][t] != "passed")
    elif res["tests"]:         # full suite: a baseline-passing test that is missing counts as broken
        covering = sorted(t for t in passing if res["tests"].get(t) != "passed")
    else:              # crashed before reporting anything: the stub broke the whole run
        covering = sorted(passing)
    if not covering:
        return {"status": "rejected_sabotage", "reason": "not_covered_by_tests", "n_covering": 0}
    if len(covering) > 0.5 * max(len(passing), 1) and len(passing) > 20:
        return {"status": "rejected_sabotage", "reason": "breaks_most_of_suite(core_infrastructure)",
                "n_covering": len(covering)}
    return {"status": "eligible", "reason": "", "n_covering": len(covering),
            "covering_tests": json.dumps(covering)}


# ---------------------------------------------------------------- tasks

def task_id_for(cfg, row):
    lang = cfg["language"]
    repo = cfg["key"].split("__", 1)[1]
    stem = re.sub(r"[^A-Za-z0-9]+", "_", Path(row["file"]).with_suffix("").as_posix()).strip("_")
    return f"{lang}__{repo}__{stem}__{row['name'].split('::')[-1].split('.')[-1]}"


def cmd_make_task(a):
    cfg = load_repo(a.repo)
    lang = langs.get(cfg["language"])
    rows = list(csv.DictReader((BENCH / "logs" / "candidates" / f"{cfg['key']}.csv").open()))
    row = next((r for r in rows if r["candidate_id"] == a.candidate), None)
    if row is None or row["status"] != "eligible":
        sys.exit(f"candidate {a.candidate} not found or not eligible")
    start = int(row["start"])
    tid = a.task_id or task_id_for(cfg, row)
    d = BENCH / "tasks" / tid
    if d.exists() and not a.force:
        sys.exit(f"{d} exists (use --force)")
    d.mkdir(parents=True, exist_ok=True)
    src = (cfg["abs_path"] / row["file"]).read_text(errors="replace").splitlines(keepends=True)
    ex = lang.extent(src, start, int(row["end"]), row["name"])
    end, suffix = ex["end"], ex["suffix"]
    ref = "".join(src[start - 1:end])[:-len(suffix)] + "\n"
    indent = re.match(r"[ \t]*", src[start - 1]).group(0)
    ext = lang.ext
    (d / f"reference{ext}").write_text(textwrap.dedent(ref) if indent else ref)
    stub_txt = lang.make_stub(src, ex, for_prompt=True) + "\n"
    (d / f"stub{ext}").write_text(textwrap.dedent(stub_txt) if indent else stub_txt)
    sabotage_txt = lang.make_stub(src, ex) + "\n"
    (d / f".sabotage{ext}").write_text(textwrap.dedent(sabotage_txt) if indent else sabotage_txt)
    (d / "context.md").write_text(lang.context(src, start, end, row["file"], [
        f for rel, f in iter_functions(cfg) if rel == row["file"]]))
    if not (d / "spec.md").exists():
        (d / "spec.md").write_text(SPEC_TEMPLATE)
    meta = {
        "task_id": tid, "repo": cfg["key"], "language": cfg["language"],
        "repo_url": cfg["url"], "tag": cfg["tag"], "commit_sha": cfg["commit_sha"],
        "release_date": cfg["release_date"], "license": cfg["license"],
        "file": row["file"], "symbol": row["long_name"], "name": row["name"],
        "start_line": start, "end_line": end, "end_suffix": suffix, "indent": indent,
        "nloc": int(row["nloc"]), "ccn": int(row["ccn"]),
        "n_covering_tests": int(row["n_covering"]),
        "covering_tests": json.loads(row["covering_tests"]),
        "bench": {"driver": None, "build_cmd": None, "run_cmd": None, "sizes": ["S", "M", "L"]},
        "spec_status": "new", "created": time.strftime("%Y-%m-%d"),
    }
    write_json(d / "task.json", meta)
    print(f"created {d.relative_to(ROOT)}")


SPEC_TEMPLATE = """# Functional specification

## 1. Component overview

## 2. Functional requirements

## 3. Input specification

## 4. Output specification

## 5. Edge cases and constraints
"""


def inject(cfg, task, impl_text):
    """Write impl_text over the task's function span in the workspace. Returns rel path."""
    rel = task["file"]
    src = (cfg["abs_path"] / rel).read_text(errors="replace").splitlines(keepends=True)
    body = impl_text.rstrip("\n") + "\n"
    if task["indent"]:
        body = textwrap.indent(textwrap.dedent(body), task["indent"], lambda l: l.strip() != "")
    body = body.rstrip("\n") + task["end_suffix"]
    new = src[:task["start_line"] - 1] + [body] + src[task["end_line"]:]
    (workspace(cfg) / rel).write_text("".join(new))
    note_written(cfg, rel)
    if task["language"] == "go":
        go_fix_imports(cfg, rel)
    return rel


def go_fix_imports(cfg, rel):
    """Run goimports on the injected Go file (applied to reference and model code alike): an import used
    only by the replaced function, or one a model forgot, must not turn into a compile error."""
    q = shlex.quote("/w/" + rel)
    rc, log, out, _ = docker_run(cfg, f"goimports -w {q} && sha256sum {q} | cut -c1-64", timeout=120)
    shutil.rmtree(out, ignore_errors=True)
    if rc != 0:
        return  # unparsable code: leave it, the build step reports the compile error
    want = log.strip().splitlines()[-1].strip()
    path = workspace(cfg) / rel
    for _ in range(100):  # wait until the host sees the container's write
        if hashlib.sha256(path.read_bytes()).hexdigest() == want:
            break
        time.sleep(0.1)
    note_written(cfg, rel)


PROMPT_TEMPLATE = """You are an expert {lang_title} developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing {lang_title} code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```{fence} code block, with no explanation.

=== SPECIFICATION ===
{spec}

=== CONTEXT ===
{context}

=== STUB ===
```{fence}
{stub}
```
"""

FENCE = {"python": "python", "javascript": "javascript", "go": "go", "rust": "rust", "java": "java", "cpp": "cpp"}


def build_prompt(task):
    d = task["dir"]
    ext = langs.get(task["language"]).ext
    return PROMPT_TEMPLATE.format(
        lang_title={"cpp": "C++", "javascript": "JavaScript"}.get(task["language"], task["language"].capitalize()),
        fence=FENCE[task["language"]], spec=(d / "spec.md").read_text().strip(),
        context=(d / "context.md").read_text().strip(), stub=(d / f"stub{ext}").read_text().rstrip())


def cmd_prompt(a):
    task = load_task(a.task)
    text = build_prompt(task)
    if a.write:
        (task["dir"] / "prompt.md").write_text(text)
        print(f"wrote {(task['dir'] / 'prompt.md').relative_to(ROOT)}")
    else:
        print(text)


def extract_code(text):
    """If text is a model reply, return the first fenced code block; otherwise return it unchanged."""
    # fences must start a line: code can itself contain ``` inside strings (e.g. Markdown generators)
    m = re.search(r"^[ \t]*```[A-Za-z0-9_+-]*[ \t]*\n(.*?)^[ \t]*```[ \t]*$", text, re.S | re.M)
    return m.group(1) if m else text


def impl_path(task, impl):
    if impl in ("reference", "stub"):
        ext = langs.get(task["language"]).ext
        return task["dir"] / (f"reference{ext}" if impl == "reference" else f".sabotage{ext}")
    return Path(impl).resolve()


def strip_comments(text, lang_name):
    if lang_name == "python":
        return re.sub(r"#[^\n]*", "", text)
    return re.sub(r"//[^\n]*", "", re.sub(r"(?s)/\*.*?\*/", "", text))


def signature_text(text, lang_name):
    """Text from the start of `text` up to the end of the first function signature (':' or '{')."""
    L = langs.get(lang_name)
    if lang_name == "python":
        m = re.search(r"^[ \t]*(async[ \t]+)?def[ \t]", text, re.M)
        if not m:
            return None, None
        lines = textwrap.dedent(text[m.start():]).splitlines(keepends=True)
        span = L.signature_span(lines, 1, "")
        if not span:
            return None, None
        li, col = span
        return text[:m.start()], "".join(lines[:li]) + lines[li][:col]
    ob = L._scan(text, 0, stop_at_open=True)
    return ("", text[:ob + 1]) if ob is not None else (None, None)


def interface_check(task, text):
    """Fixed rules applied before any test runs. Returns (label or None, detail)."""
    lang_name = task["language"]
    if not text.strip():
        return "no_code", "empty reply"
    ext = langs.get(lang_name).ext
    stub = (task["dir"] / f"stub{ext}").read_text()
    _, want = signature_text(stub, lang_name)
    lead, got = signature_text(text, lang_name)
    if got is None:
        return "no_code", "no function definition found"
    norm = lambda t: re.sub(r"\s+", "", strip_comments(t, lang_name))
    if norm(got) != norm(want):
        if norm(got).endswith(norm(want)) or norm(lead or "").strip():
            return "format_violation", "code before the function (imports, helpers or decorators)"
        return "interface_violation", f"signature differs from the stub: {norm(got)[:200]}"
    if lang_name == "python":
        import ast
        try:
            tree = ast.parse(textwrap.dedent(text))
        except SyntaxError as e:
            return "compile_error", f"SyntaxError: {e}"
        extra = [type(n).__name__ for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        defs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if extra or len(defs) != 1:
            return "format_violation", f"extra top-level code: {extra or [d.name for d in defs]}"
    else:
        L = langs.get(lang_name)
        ob = L._scan(text, 0, stop_at_open=True)
        cb = L._scan(text, ob)
        if cb is None:
            return "compile_error", "unbalanced braces"
        tail = strip_comments(text[cb + 1:], lang_name).strip().lstrip(";").strip()
        if tail:
            return "format_violation", f"code after the function: {tail[:120]}"
    return None, ""


def evaluate(task, impl, with_diff=True):
    cfg = load_repo(task["repo"])
    base = load_baseline(cfg["key"])
    passing = set(base["passing"])
    text = extract_code(impl_path(task, impl).read_text())
    if impl not in ("reference", "stub"):
        label, detail = interface_check(task, text)
        if label:
            return {"impl": str(impl), "status": label, "detail": detail, "compiled": None, "passed": False}
    with RepoLock(cfg["key"]):
        rel = inject(cfg, task, text)
        try:
            res = run_tests(cfg)
            diff = bench_run(cfg, task, size="S", repeat=1) if with_diff and task["bench"].get("run_cmd") else None
        finally:
            restore_file(cfg, rel)
    if res["build_failed"]:
        return {"impl": str(impl), "status": "compile_error", "compiled": False, "passed": False,
                "log_tail": res["log_tail"]}
    if res["crashed"]:
        return {"impl": str(impl), "status": "crashed", "compiled": True, "passed": False, "rc": res["rc"],
                "log_tail": res["log_tail"]}
    if res["timed_out"] and not res["tests"]:
        return {"impl": str(impl), "status": "timeout", "compiled": True, "passed": False,
                "log_tail": res["log_tail"]}
    # A doctest that lives in the replaced function's own docstring disappears when the model writes the
    # function without that docstring: a *missing* doctest of the target is not a failure.
    short = task["name"].split("::")[-1].split(".")[-1]
    own_doctest = lambda t: (task["language"] == "python" and t not in res["tests"]
                             and t.split("::")[-1].endswith("." + short))
    regress = sorted(t for t in passing if res["tests"].get(t) != "passed" and not own_doctest(t))
    cover_fail = sorted(set(task["covering_tests"]) & set(regress))
    out = {"impl": str(impl), "compiled": True, "n_regressions": len(regress),
           "covering_failed": len(cover_fail), "covering_total": len(task["covering_tests"]),
           "regressions": regress[:50]}
    if diff is not None:
        ref = json.loads((task["dir"] / "bench" / "expected.json").read_text()) \
            if (task["dir"] / "bench" / "expected.json").exists() else {}
        out["diff_digest"] = diff.get("output_digest")
        out["diff_ok"] = (diff.get("output_digest") == ref.get("S")) if ref else None
        if diff.get("error"):
            out["diff_error"] = diff["error"]
        if diff.get("timed_out"):
            out["diff_timed_out"] = True
    out["passed"] = out["n_regressions"] == 0 and out.get("diff_ok") is not False and not res["timed_out"]
    if out["passed"]:
        out["status"] = "passed"
    elif res["timed_out"] or out.get("diff_timed_out"):
        out["status"] = "timeout"
    elif out["n_regressions"]:
        out["status"] = "failed_tests"
    else:
        out["status"] = "wrong_output"
    return out


def cmd_eval(a):
    task = load_task(a.task)
    print(json.dumps(evaluate(task, a.impl), indent=2))


# ---------------------------------------------------------------- bench

def ensure_workload(task):
    """Generate bench/workload_<size>.* with the task's seeded generator (host python3, stdlib only)."""
    bdir = task["dir"] / "bench"
    if all(list(bdir.glob(f"workload_{s}.*")) for s in task["bench"]["sizes"]):
        return
    p = subprocess.run([sys.executable, str(bdir / "gen_workload.py"), str(bdir)], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"gen_workload.py failed: {p.stderr[-2000:]}")


def workload_digest(task):
    h = hashlib.sha256()
    for f in sorted((task["dir"] / "bench").glob("workload_*")):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()


CHECK_TIMEOUT = 120  # seconds, per output-check run


def bench_run(cfg, task, size="S", repeat=1, mode="check", timeout=None):
    """Run the task's bench driver in the (already injected) workspace.

    Driver contract (see BUILDER_GUIDE.md): argv = <size> <repeat> <mode>, prints one JSON line:
      mode=check -> {"cases": int, "output_digest": "<sha256 of canonical outputs>"}
      mode=time  -> {"cases": int, "repeat": int, "elapsed_s": float}
    """
    ensure_workload(task)
    b = task["bench"]
    tdir_in = "/task"
    cmd = fill(b["run_cmd"], size=size, repeat=repeat, mode=mode, task=tdir_in)
    if mode == "time":  # peak RSS / process time of the measured command only (build step excluded)
        cmd = f"/opt/tctools/tcmeasure bash -c {shlex.quote(cmd)}"
    if b.get("build_cmd"):
        cmd = f"( {fill(b['build_cmd'], task=tdir_in)} ) && ( {cmd} )"
    # an output check of the reference takes seconds (L pass <= ~5 s), so a long check means an endless loop
    rc, log, out, secs = docker_run(cfg, cmd, timeout=timeout or (CHECK_TIMEOUT if mode == "check" else 1800),
                                    extra_mounts=[(str(task["dir"]), tdir_in)])
    shutil.rmtree(out, ignore_errors=True)
    key = "output_digest" if mode == "check" else "elapsed_s"
    meas = {}
    for line in log.splitlines():
        if line.startswith('{"tcmeasure"'):
            try:
                meas = json.loads(line)["tcmeasure"]
            except ValueError:
                pass
    for line in reversed(log.strip().splitlines()):
        line = line.strip()
        if line.startswith("{") and key in line:
            try:
                r = json.loads(line)
                r["wall_container_s"] = round(secs, 3)
                if meas:
                    r["peak_rss_kb"] = meas["peak_rss_kb"]
                    r["process_wall_s"] = meas["wall_s"]
                return r
            except ValueError:
                pass
    return {"error": f"driver failed rc={rc}", "timed_out": log.startswith("TIMEOUT after"), "log_tail": log[-3000:]}


def cmd_bench(a):
    task = load_task(a.task)
    cfg = load_repo(task["repo"])
    text = extract_code(impl_path(task, a.impl).read_text())
    with RepoLock(cfg["key"]):
        rel = inject(cfg, task, text)
        try:
            r = bench_run(cfg, task, size=a.size, repeat=a.repeat, mode="time")
            if a.min_time and not r.get("error") and r["elapsed_s"] < a.min_time:
                # calibrate like timeit's autorange: repeat until one measurement lasts >= min_time
                rep = max(1, math.ceil(1.1 * a.min_time / max(r["elapsed_s"], 1e-6) * a.repeat))
                r = bench_run(cfg, task, size=a.size, repeat=rep, mode="time")
            if not r.get("error"):
                r["per_pass_s"] = r["elapsed_s"] / r["repeat"]
        finally:
            restore_file(cfg, rel)
    print(json.dumps(r, indent=2))


# ---------------------------------------------------------------- run (gated pipeline)

def static_metrics(text, lang_name):
    import tempfile
    ext = langs.get(lang_name).ext
    with tempfile.NamedTemporaryFile("w", suffix=ext, delete=False) as fh:
        fh.write(text)
    try:
        fs = lizard.analyze_file(fh.name).function_list
    finally:
        os.unlink(fh.name)
    if not fs:
        return {}
    f = max(fs, key=lambda x: x.nloc)
    return {"nloc": f.nloc, "ccn": f.cyclomatic_complexity, "tokens": f.token_count}


def run_pipeline(task, impl, sizes=("S", "M", "L"), min_time=1.0, reps=3):
    """Stage 1: correctness gate (interface check, original tests, S output check).
    Stage 2 (only if correct): M/L output checks, then calibrated timing + peak memory per size."""
    rec = {"task_id": task["task_id"], "impl": str(impl), "time": time.strftime("%Y-%m-%dT%H:%M:%S")}
    ev = evaluate(task, impl)
    rec["status"] = ev["status"]
    rec["correctness"] = {k: ev.get(k) for k in ("status", "detail", "compiled", "n_regressions", "covering_failed",
                                                 "covering_total", "diff_ok", "regressions")}
    text = extract_code(impl_path(task, impl).read_text())
    rec["static"] = static_metrics(text, task["language"])
    if not ev["passed"]:
        return rec
    cfg = load_repo(task["repo"])
    exp = json.loads((task["dir"] / "bench" / "expected.json").read_text())
    rec["efficiency"] = {}
    with RepoLock(cfg["key"]):
        rel = inject(cfg, task, text)
        try:
            for size in sizes:
                chk = bench_run(cfg, task, size=size, mode="check")
                if chk.get("timed_out"):
                    rec["status"] = "timeout"
                    rec["correctness"]["diff_failed_size"] = size
                    return rec
                if chk.get("output_digest") != exp.get(size):
                    rec["status"] = "wrong_output"
                    rec["correctness"]["diff_failed_size"] = size
                    return rec
                probe = bench_run(cfg, task, size=size, repeat=1, mode="time")
                if probe.get("error"):
                    rec["status"] = "crashed"
                    return rec
                rep_n = max(1, math.ceil(1.1 * min_time / max(probe["elapsed_s"], 1e-6)))
                runs = [bench_run(cfg, task, size=size, repeat=rep_n, mode="time") for _ in range(reps)]
                per_pass = sorted(r["elapsed_s"] / r["repeat"] for r in runs if not r.get("error"))
                rss = sorted(r.get("peak_rss_kb", 0) for r in runs if not r.get("error"))
                rec["efficiency"][size] = {"repeat": rep_n, "runs": len(per_pass),
                                           "per_pass_s_median": per_pass[len(per_pass) // 2] if per_pass else None,
                                           "per_pass_s_all": per_pass,
                                           "peak_rss_kb_median": rss[len(rss) // 2] if rss else None}
        finally:
            restore_file(cfg, rel)
    return rec


def cmd_run(a):
    task = load_task(a.task)
    rec = run_pipeline(task, a.impl, sizes=a.sizes.split(","), min_time=a.min_time, reps=a.reps)
    if a.label:
        rec["label"] = a.label
    line = json.dumps(rec)
    if a.out:
        with open(a.out, "a") as fh:
            fh.write(line + "\n")
    print(json.dumps(rec, indent=2))


# ---------------------------------------------------------------- check

SPEC_SECTIONS = ["Component overview", "Functional requirements", "Input specification",
                 "Output specification", "Edge cases"]


def code_only(text, lang_name):
    """Reference code with comments, docstrings and string literals removed."""
    if lang_name == "python":
        text = re.sub(r'(?s)("""|\'\'\')(.*?)\1', " ", text)
        text = re.sub(r"#[^\n]*", " ", text)
    else:
        text = re.sub(r"(?s)/\*.*?\*/", " ", text)
        text = re.sub(r"//[^\n]*", " ", text)
    return re.sub(r'"(\\.|[^"\\\n])*"|\'(\\.|[^\'\\\n])*\'', " ", text)


def spec_leakage(spec, ref, lang_name, stub=""):
    """Longest run of identical code tokens shared by spec and the reference *body*
    (identifiers + operators; the signature, which the model sees anyway, is excluded)."""
    tok = lambda s: re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\S", s)
    a, b = tok(spec), tok(code_only(ref, lang_name))
    sig = tok(code_only(stub, lang_name))
    k = 0
    while k < min(len(sig), len(b)) and sig[k] == b[k]:
        k += 1
    b = b[k:]
    best, prev = 0, {}
    for x in a:
        cur = {}
        for j, y in enumerate(b):
            if x == y:
                cur[j] = prev.get(j - 1, 0) + 1
                best = max(best, cur[j])
        prev = cur
    return best


def check_task(tid, run=True):
    task = load_task(tid)
    d = task["dir"]
    ext = langs.get(task["language"]).ext
    problems = []
    for f in ["task.json", "spec.md", f"reference{ext}", f"stub{ext}", "context.md"]:
        if not (d / f).exists():
            problems.append(f"missing {f}")
    spec = (d / "spec.md").read_text() if (d / "spec.md").exists() else ""
    for s in SPEC_SECTIONS:
        if s.lower() not in spec.lower():
            problems.append(f"spec missing section '{s}'")
    if len(re.sub(r"\s+", " ", spec)) < 400:
        problems.append("spec too short (<400 chars)")
    leak = spec_leakage(spec, (d / f"reference{ext}").read_text(), task["language"],
                        (d / f"stub{ext}").read_text() if (d / f"stub{ext}").exists() else "") if spec else 0
    if leak >= 12:
        problems.append(f"spec shares a {leak}-token run with the reference code (leakage)")
    if not task["bench"].get("run_cmd"):
        problems.append("bench.run_cmd not set")
    if not (d / "bench" / "expected.json").exists():
        problems.append("bench/expected.json missing (run: tc.py expect <task>)")
    result = {"task": tid, "leak_tokens": leak}
    if run:
        ref = evaluate(task, "reference")
        stub = evaluate(task, "stub", with_diff=False)
        result["reference"] = {k: ref.get(k) for k in ("compiled", "passed", "n_regressions", "diff_ok")}
        result["stub"] = {k: stub.get(k) for k in ("compiled", "passed", "covering_failed")}
        if not ref.get("passed"):
            problems.append(f"reference does not pass: {ref.get('regressions', ref.get('log_tail', ''))[:5]}")
        if stub.get("passed"):
            problems.append("stub passes the tests (task is not discriminating)")
    result["problems"] = problems
    result["ok"] = not problems
    return result


def cmd_check(a):
    ids = sorted(p.name for p in (BENCH / "tasks").iterdir() if (p / "task.json").exists()) if a.all else [a.task]
    if a.repo:
        ids = [i for i in ids if load_task(i)["repo"] == a.repo]
    bad = 0
    for tid in ids:
        r = check_task(tid, run=not a.static)
        bad += not r["ok"]
        print(json.dumps(r))
    print(f"{len(ids) - bad}/{len(ids)} tasks ok")


def cmd_expect(a):
    """Record reference output digests for every workload size (the differential oracle)."""
    task = load_task(a.task)
    cfg = load_repo(task["repo"])
    exp = {}
    text = impl_path(task, "reference").read_text()
    with RepoLock(cfg["key"]):
        rel = inject(cfg, task, text)
        try:
            for size in task["bench"]["sizes"]:
                r1 = bench_run(cfg, task, size=size)
                r2 = bench_run(cfg, task, size=size)
                if r1.get("error") or r1.get("output_digest") != r2.get("output_digest"):
                    sys.exit(f"size {size}: driver error or non-deterministic output: {r1} {r2}")
                exp[size] = r1["output_digest"]
                t = bench_run(cfg, task, size=size, repeat=1, mode="time")
                exp[f"{size}_elapsed_s"] = t.get("elapsed_s")
            exp["workload_sha256"] = workload_digest(task)
        finally:
            restore_file(cfg, rel)
    write_json(task["dir"] / "bench" / "expected.json", exp)
    print(json.dumps(exp, indent=2))


# ---------------------------------------------------------------- select / summary

def cmd_select(a):
    """Deterministic task selection: eligible, >=2 covering tests, not nested/anonymous,
    ranked by cyclomatic complexity then size, preferring at most --per-file per source file, top --k."""
    cfg = load_repo(a.repo)
    rows = list(csv.DictReader((BENCH / "logs" / "candidates" / f"{cfg['key']}.csv").open()))
    ok = []
    for r in rows:
        if r["status"] != "eligible" or int(r["n_covering"] or 0) < 2:
            continue
        short = r["name"]
        if cfg["language"] == "python" and "." in short:
            continue  # nested function: not callable on its own
        if "anonymous" in short.lower() or short in ("(anonymous)", "function"):
            continue
        ok.append(r)
    ok.sort(key=lambda r: (-int(r["ccn"]), -int(r["nloc"]), r["candidate_id"]))
    picked, per_file = [], {}
    for r in ok:
        if per_file.get(r["file"], 0) >= a.per_file:
            continue
        picked.append(r)
        per_file[r["file"]] = per_file.get(r["file"], 0) + 1
        if len(picked) >= a.k:
            break
    for r in ok:  # few source files: fill the remaining slots by rank
        if len(picked) >= a.k:
            break
        if r not in picked:
            picked.append(r)
    out = BENCH / "logs" / "selected" / f"{cfg['key']}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(r["candidate_id"] + "\n" for r in picked))
    print(f"{cfg['key']}: {len(ok)} selectable, picked {len(picked)} -> {out.relative_to(ROOT)}")
    for r in picked:
        print("  " + r["candidate_id"], f"ccn={r['ccn']} nloc={r['nloc']} covering={r['n_covering']}")


def cmd_summary(a):
    rows = []
    for d in sorted((BENCH / "tasks").iterdir()):
        if not (d / "task.json").exists():
            continue
        t = json.loads((d / "task.json").read_text())
        exp = json.loads((d / "bench" / "expected.json").read_text()) if (d / "bench" / "expected.json").exists() else {}
        rows.append({k: t.get(k) for k in ("task_id", "language", "repo", "tag", "release_date", "license",
                                           "file", "name", "nloc", "ccn", "n_covering_tests", "spec_status")}
                    | {"L_elapsed_s": exp.get("L_elapsed_s")})
    out = BENCH / "tasks.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    by = {}
    for r in rows:
        by.setdefault(r["language"], {}).setdefault(r["repo"], 0)
        by[r["language"]][r["repo"]] += 1
    print(f"{len(rows)} tasks -> {out.relative_to(ROOT)}")
    for l, reps in sorted(by.items()):
        print(f"  {l}: {sum(reps.values())} tasks  " + ", ".join(f"{k.split('__')[1]}={v}" for k, v in sorted(reps.items())))


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("setup"); p.add_argument("repo"); p.set_defaults(fn=cmd_setup)
    p = sp.add_parser("baseline"); p.add_argument("repo"); p.set_defaults(fn=cmd_baseline)
    p = sp.add_parser("candidates"); p.add_argument("repo"); p.add_argument("--max", type=int, default=0)
    p.add_argument("--until", type=int, default=0,
                   help="stop sabotage runs once this many selectable candidates were found (ranked by CCN)")
    p.set_defaults(fn=cmd_candidates)
    p = sp.add_parser("make-task"); p.add_argument("repo"); p.add_argument("candidate")
    p.add_argument("--task-id"); p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_make_task)
    p = sp.add_parser("eval"); p.add_argument("task"); p.add_argument("impl"); p.set_defaults(fn=cmd_eval)
    p = sp.add_parser("bench"); p.add_argument("task"); p.add_argument("impl")
    p.add_argument("--size", default="S"); p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--min-time", type=float, default=0.0,
                   help="raise --repeat until one measurement lasts at least this many seconds")
    p.set_defaults(fn=cmd_bench)
    p = sp.add_parser("expect"); p.add_argument("task"); p.set_defaults(fn=cmd_expect)
    p = sp.add_parser("check"); p.add_argument("task", nargs="?"); p.add_argument("--all", action="store_true")
    p.add_argument("--repo"); p.add_argument("--static", action="store_true"); p.set_defaults(fn=cmd_check)
    p = sp.add_parser("select"); p.add_argument("repo"); p.add_argument("--k", type=int, default=10)
    p.add_argument("--per-file", type=int, default=4); p.set_defaults(fn=cmd_select)
    p = sp.add_parser("summary"); p.set_defaults(fn=cmd_summary)
    p = sp.add_parser("run"); p.add_argument("task"); p.add_argument("impl")
    p.add_argument("--label", help="e.g. model name / sample id, stored in the record")
    p.add_argument("--out", help="append the JSON record to this .jsonl file")
    p.add_argument("--sizes", default="S,M,L"); p.add_argument("--min-time", type=float, default=1.0)
    p.add_argument("--reps", type=int, default=3); p.set_defaults(fn=cmd_run)
    p = sp.add_parser("prompt"); p.add_argument("task"); p.add_argument("--write", action="store_true")
    p.set_defaults(fn=cmd_prompt)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
