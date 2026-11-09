# Time Capsulo: data format

## Folder layout

```
tasks.jsonl            all 260 tasks, one JSON object per line (prompt + metadata; no reference code)
index.csv              one row per task (same metadata, as a table)
repos.csv              the 30 pinned library snapshots (see below)
benchmark/tasks/<task_id>/    the files of one task
benchmark/repos/<repo>.json   how each library is built and tested
benchmark/repos/<repo>.baseline.json   which of its tests pass with the original code
benchmark/lockfiles/   exact Cargo.lock files (Rust)
benchmark/selection_logs/   skipped / added / retired candidate functions, with reasons
benchmark/blind_check/      evidence that each specification is sufficient
harness/               the evaluation tool and the toolchain Dockerfiles
```

`<task_id>` = `<language>__<repo>__<file path with / and . replaced by _>__<function>`, for example
`cpp__pugixml__src_pugixml__sort`. Languages: `python`, `go`, `javascript`, `rust`, `java`, `cpp`.

## `tasks.jsonl` and `index.csv`

| Field | Meaning |
|---|---|
| `task_id` | unique id (also the folder name) |
| `language`, `repo` | language and library name |
| `repo_url`, `tag`, `commit_sha`, `release_date` | exact source version (a 2018–2019 release) |
| `license` | licence of the library (SPDX id) |
| `file`, `function` | source file in the library and the function to implement |
| `nloc`, `ccn` | lines of code and cyclomatic complexity of the original function (`lizard`) |
| `covering_tests` | number of the library's own tests that run the function (each task has at least 2) |
| `spec_status` | `checked-v1.0` = the specification passed the automatic checks (leakage check, blind solvability test) for dataset version 1.0 |
| `prompt` (jsonl only) | **the exact text to send to the model** (instructions, specification, context, stub) |
| `stub` (jsonl only) | the signature with an empty body (already inside the prompt) |
| `leak_tokens` (csv only) | longest run of identical code tokens shared by the specification and the original code (all < 12) |

## Files of one task (`benchmark/tasks/<task_id>/`)

| File | Content | Shown to the model? |
|---|---|---|
| `prompt.md` | the assembled prompt | **yes** |
| `spec.md`, `context.md`, `stub.<ext>` | the parts of the prompt | (inside the prompt) |
| `reference.<ext>` | the original human function | **no, never** |
| `task.json` | provenance, line range in the source file, `covering_tests` (names), benchmark commands | no |
| `bench/` | seeded workload generator (`gen_workload.py`, sizes S/M/L), the timing driver, `expected.json`, `README.md` (what the workload does) | no |

`<ext>` is `py`, `go`, `js`, `rs`, `java` or `cpp`. The S/M/L workload files are generated on the first run from
`bench/gen_workload.py` (seeded, deterministic) and are checked against `bench/expected.json`
(`S`, `M`, `L`: output fingerprints of the original code; `*_elapsed_s`: its time when the task was built;
`workload_sha256`: fingerprint of the workload files).

## `repos.csv`

`language, name, github_repo, tag, commit_sha, release_date, url, local_path, tree_sha256`. `setup.sh` downloads each
tag from GitHub and refuses the snapshot if its content hash (`tree_sha256`: sha256 over the sorted relative
paths and file contents) differs.

## `benchmark/repos/<repo>.baseline.json`

`n_tests` (tests run), `passing` (the stable passing tests: an answer must keep all of them passing), `flaky`
(tests that were excluded because they vary between runs), `failing_at_baseline`, `secs` (run times of the
baseline runs; the first, cold run includes compiling).

## Result records (`results.jsonl`, one line per evaluated answer)

| Field | Meaning |
|---|---|
| `task_id`, `label`, `time` | task, the name you gave with `--label`, timestamp |
| `status` | the single outcome label: `passed`, `failed_tests`, `wrong_output`, `compile_error`, `timeout`, `crashed`, `interface_violation`, `format_violation`, `no_code` |
| `correctness` | `compiled`, `n_regressions` (original tests that now fail), `regressions` (their names), `covering_failed` / `covering_total`, `diff_ok` (outputs equal the original on S/M/L), `detail` |
| `static` | size and complexity of the answer's code |
| `efficiency` | only for `passed` answers: per size S/M/L, calibrated runtime (median of repeats), peak memory, and all individual timings |

`benchmark/blind_check/*results*.jsonl` use the same record format.

## Reproducibility details

- Each library is pinned by tag, commit and content hash; the toolchains are era-appropriate Docker images
  (Python 3.7, Go 1.13, Node.js 10, Rust 1.40, Java 8, GCC 9) whose base images are pinned by digest.
- Test-only dependencies are resolved as of each library's release date (JavaScript), fixed by lockfiles (Rust) or taken
  from the library's own build files (Go, Java); the package registries must be reachable during `setup.sh`.
- Answers are judged with networking disabled in the container.
