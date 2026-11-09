# Time Capsulo Benchmark: User Guide (Python + Go + JavaScript + Rust + Java + C++ release)

Time Capsulo measures whether code written by an AI model is **as correct as, and more or less efficient than,
code written by humans before AI coding assistants existed**.

Each of the **260 tasks** is one real function from a popular library released in 2018–2019:
**50 Python tasks**, **38 Go tasks**, **40 JavaScript tasks** and **32 Rust tasks**, **50 Java tasks** and **50 C++ tasks** (5 libraries per language). The model re-writes that function from a
specification. Its code is put back into the original library and judged by:

1. **Correctness:** the library's **own 2018–2019 test suite**, plus an exact comparison of outputs with the
   original human code on generated inputs.
2. **Efficiency** (correct code only): runtime and peak memory on small, medium and large inputs, compared
   with the human code measured the same way.

This guide covers installation, generating model answers, evaluation and reading the results.

---

## 1. Requirements

| Item | Needed for | Notes |
|---|---|---|
| Docker (Desktop or Engine), running | everything | All library code runs in containers with the toolchains of the time: Python 3.7, Go 1.13, Node.js 10, Rust 1.40, Java 8 (Maven 3.6), C++ (GCC 9.4, CMake 3.16). Give Docker ≥ 4 GB RAM. |
| Python ≥ 3.8 on the host | the harness | Runs on the host; only needs `lizard` (installed by setup). |
| ~15 GB free disk | images, sources, Go module cache, npm test dependencies, Rust build caches (about 2.5 GB), Maven cache (a few hundred MB), C++ build volumes (about 1–2 GB; nlohmann/json's sources alone are 260 MB) | |
| Internet | setup only | Evaluation runs with networking disabled inside containers. |
| Bare-metal Linux, Intel/AMD CPU | **energy** only (optional) | See §7. Runtime and memory work on any Docker host, including macOS and Windows. |

Tested on macOS (Apple Silicon) with Docker Desktop. Linux x86-64 is the intended platform for energy measurement.

---

## 2. Setup (one command, about 45–90 minutes; Rust and C++ compile their dependencies and test suites)

```bash
cd time_capsulo_six_languages
./setup.sh                 # all six languages
./setup.sh go rust java    # or a subset: python | go | javascript | rust | java | cpp
```

What it does:

1. Creates `.venv/` and installs `lizard`.
2. Builds the Docker images `tc-python37` (Python 3.7 + pytest 5.3.5), `tc-go` (Go 1.13 + a pinned
   `goimports`), `tc-javascript` (Node.js 10 + npm 6 + test-runner adapters) `tc-rust` (Rust 1.40) `tc-java` (Maven 3.6 on Amazon Corretto 8) and `tc-cpp` (Ubuntu 20.04 with GCC 9.4 and CMake 3.16). All base images are pinned by digest.
3. Compiles the measurement helper `harness/tools/tcmeasure` for your CPU architecture.
4. Downloads the 30 pinned library snapshots into `repos/` and **verifies each one by content hash** (`repos.csv` → `tree_sha256`).
5. Creates a working copy of each library (`.work/`) and installs its pinned test-only dependencies. For Go,
   the modules pinned by each library's own `go.mod`/`go.sum` are downloaded into the Docker volume
   `tc-cache-gomod`; tests then run offline. For JavaScript, the test-only npm packages are installed with
   their versions resolved as of each library's release date (`npm --before`). For Rust, the exact dependency
   versions come from the shipped lockfiles in `benchmark/lockfiles/` (`cargo fetch --locked`); the Rust
   build caches live in the Docker volumes `tc-cache-cargo` and `tc-target-<library>`.

**Check the installation.** This runs the original code and a deliberately broken stub through the tests:

```bash
.venv/bin/python harness/tc.py check python__more-itertools__more_itertools_more__windowed
.venv/bin/python harness/tc.py check go__go-humanize__comma__Comma
.venv/bin/python harness/tc.py check javascript__qs__lib_stringify__stringify
.venv/bin/python harness/tc.py check rust__strsim-rs__src_lib__osa_distance
```

Expected: `"ok": true`, with the reference passing and the stub failing. To check all 210 tasks
(Python 15–30 minutes, Go and JavaScript about 15 minutes each, Rust 30–60 minutes because every task recompiles the crate, Java about 20–30 minutes, C++ about 1 hour because header changes recompile the test suites):

```bash
.venv/bin/python harness/tc.py check --all
```

---

## 3. What is in the release

```
QUICKSTART.md        shortest path: use the tasks, or score a model
README.md            overview, verification summary, limitations
USER_GUIDE.md        this file
DATA_FORMAT.md       every file and field of the dataset and of the result records
tasks.jsonl          all 260 tasks, one JSON object per line (prompt + metadata)
CHECKSUMS.sha256     sha256 of every file in this folder (verify with `shasum -a 256 -c CHECKSUMS.sha256`)
NOTICE.md, LICENSE, CITATION.cff   licences of the 30 libraries, licence of this dataset, how to cite
index.csv            one row per task (repo, version, commit, file, function, size, complexity, ...)
repos.csv            pinned sources: GitHub repo, tag, commit SHA, release date, content hash
setup.sh             installation
harness/
  tc.py              the evaluation tool (run `tc.py -h`)
  langs.py           code-extraction helpers
  summarize.py       per-model results table
  fetch_repos.py     downloads + verifies the library snapshots
  docker/            toolchain images: Python 3.7, Go 1.13, Node.js 10, Rust 1.40, Java 8, C++ GCC 9 (+ test-runner adapters)
  tools/tcmeasure.c  peak-memory / time helper (compiled by setup)
  check_machine.sh   checks whether a Linux machine can measure energy
benchmark/
  repos/             per-library test configuration + baseline (stable passing tests)
  lockfiles/         exact Cargo.lock for each Rust library
  tasks/<task_id>/   the 260 tasks (python__*, go__*, javascript__*, rust__*, java__*, cpp__*)
  blind_check/       evidence that each spec is sufficient (see README)
  selection_logs/    every skipped, added or retired candidate function, with the reason (per language)
```

### One task

| File | Content | Shown to the model? |
|---|---|---|
| `prompt.md` | **The exact prompt.** Instructions + specification + context + stub | **Yes: send this verbatim** |
| `spec.md` | What the function must do: requirements, inputs, outputs, errors, edge cases, examples | (inside the prompt) |
| `stub.<ext>` | The exact signature with an empty body | (inside the prompt) |
| `context.md` | Imports and other functions available in the same file; object fields for methods | (inside the prompt) |
| `reference.<ext>` | The original human code (2018–2019) | **No, never show it to the model** |
| `task.json` | Source location, metrics, covering tests, benchmark commands | No |
| `bench/` | Seeded input generator (S/M/L), benchmark driver, reference output fingerprints | No |

Task IDs look like `<language>__<repo>__<file path>__<function>`, e.g.
`python__requests__requests_utils__parse_header_links`, `go__gjson__gjson__ForEach` or
`javascript__lodash__lodash__truncate` or `rust__regex__src_expand__find_cap_ref`.

**Go specifics.**
- After the model's function is inserted, `goimports` (pinned) fixes the file's import list, for the
  human code and every model alike. So a model doesn't fail just because a package it uses isn't imported, or
  an import is left unused.
- Go benchmark drivers are compiled as part of the build, so the reported runtime and memory cover only running
  the code, never compiling it.
- Each Go test runs in its own process (`go-test-each`). A panicking answer only fails the tests that reach it.

**JavaScript specifics.**
- Answers are plain functions written in the library's own style. lodash and qs are ES5-era code; validator.js
  and moment's `src/` use ES modules and are transpiled by the libraries' own 2019 build setup.
- Module-private functions are benchmarked through a public function that calls them (e.g. lodash `baseClone`
  through `_.cloneDeep`). The task's `bench/README.md` says which one.
- moment results never depend on today's date: the drivers fix `moment.now` to 2019-01-21, and the
  container's time zone is UTC.

**Rust specifics.**
- Answers are plain functions (methods go inside their `impl`, exactly as in the stub). Do not add `use` lines or
  helpers outside the function; the prompt says so. You may use the imports and functions listed in the task's
  context.
- Each evaluation recompiles the library crate with your function inserted, so it takes longer than the other
  languages (about 1–3 minutes per answer; the regex and clap suites are the slowest).
- Dependencies are fixed by lockfiles, so setup downloads exactly the crates they list; later runs are offline.
- A compile error is reported as `compile_error`, with the compiler's message in the result record.

**C++ specifics.**
- Answers are plain functions or member functions (the complete function, exactly as in the stub). Do not add `#include` lines, helper functions or classes; the prompt says so. You may use the declarations listed in the task's context. Where the function is a method or a template, the declaration line above the stub is not part of your answer.
- Setup builds each library's test suite once into a Docker volume (`tc-build-<name>`), so the first `check` of a C++ library is the slowest (about 12 s to 2 minutes in a clean-copy test, longer on a loaded machine); later evaluations rebuild only what changed. An evaluation takes about 10 seconds (pugixml, double-conversion) to 3 minutes (nlohmann/json and fmt, whose headers are included by every test).
- A compile error is reported as `compile_error`; the compiler's output is in the result record.

**Java specifics.**
- Answers are plain methods (inside their class, exactly as in the stub). Do not add `import` lines or helper methods;
  the prompt says so. You may use the imports and methods listed in the task's context.
- Setup downloads the Maven dependencies once (internet needed); evaluations then run offline.
- An evaluation takes about 10–60 seconds per answer (commons-lang has the largest suite, about 20 s per run, and every evaluation recompiles the library); passing answers are then timed on top of that.
- A compile error is reported as `compile_error`; the compiler's output is in the result record.

---

## 4. Evaluating a model, step by step

### Step 1: Generate answers

Send each task's `prompt.md` to your model **unchanged**. Save the raw reply text as
`replies/<model>/<task_id>.md`. The reply may contain explanation text; the harness takes the code block from it.

Example with any chat-completion API. Adapt `ask()` to your provider, or to a local model:

```python
# generate.py
import pathlib, sys

MODEL = sys.argv[1]
out = pathlib.Path("replies") / MODEL
out.mkdir(parents=True, exist_ok=True)

def ask(prompt: str) -> str:
    # Call your model here, with temperature 0 for the main result. Return the reply text.
    raise NotImplementedError

for task in sorted(pathlib.Path("benchmark/tasks").iterdir()):
    target = out / f"{task.name}.md"
    if not target.exists():
        target.write_text(ask((task / "prompt.md").read_text()))
```

If you paste prompts into a web chat interface, save each reply the same way. Record the model's
exact version and the date, because web interfaces change without notice.

**Recommended protocol** (report it in your paper):
- **Temperature 0**, one answer per task, for the main result.
- A **context window of at least 16,384 tokens**: the longest prompts we measured are about 7,000 tokens, and answers need room too.
- Optionally, *k* extra samples per task at your usual temperature, saved as `replies/<model>_s1/`, `_s2/`, …, to report pass@k and the spread in efficiency.
- **No retries**, or one fixed retry rule applied to every model in the same way.
- Keep every raw reply; results can always be re-scored from them.

### Step 2: Measure the human baseline (once)

```bash
for t in $(ls benchmark/tasks); do
  .venv/bin/python harness/tc.py run $t reference --label human --out results.jsonl
done
```

### Step 3: Evaluate the model's answers

```bash
for f in replies/MyModel/*.md; do
  .venv/bin/python harness/tc.py run $(basename $f .md) $f --label MyModel --out results.jsonl
done
```

For each answer, `run` works in two stages:

1. **Correctness gate:**
   - **Interface/format check:** the code must define exactly the stubbed function, with the same signature, and nothing outside it.
   - **The library's original tests:** every test that passes with the human code must still pass.
   - **Output check:** on the S, M and L inputs, the outputs must be identical to the human code's.
2. **Efficiency (correct answers only):** per input size, runtime is calibrated so that each measurement lasts at least `--min-time` seconds (default 1.0). It is repeated `--reps` times (default 3) and the median is reported, together with peak memory (RSS).

Each answer gets exactly **one outcome label**:

| Label | Meaning |
|---|---|
| `passed` | Correct. Efficiency was measured. |
| `failed_tests` | One or more original tests fail. |
| `wrong_output` | Tests pass, but outputs differ from the human code on generated inputs. |
| `compile_error` | Syntax error or unparsable code; for Go, the package does not build with the answer inserted. |
| `timeout` | The test run, or an output check (limit 120 s, the human code needs seconds), exceeded its time limit: e.g. an infinite loop. |
| `crashed` | The process was killed (e.g. out of memory: the container is limited to 4 GB). |
| `interface_violation` | The function name or signature differs from the stub. |
| `format_violation` | Code outside the function (module-level imports, helper functions). Imports *inside* the function are allowed. |
| `no_code` | Empty reply, refusal, or no function found. |

### Step 4: Summarise

```bash
.venv/bin/python harness/summarize.py results.jsonl
```

Output per model:
- pass rate and outcome counts;
- on tasks where both the model and the human code are correct, the **geometric-mean ratio of runtime and of peak memory versus the human code**, per input size. A ratio below 1 means the model's code was faster or used less memory.

Every record in `results.jsonl` also holds the per-test details, the static metrics (lines of code, complexity) of the answer, and all individual timings, for your own statistics. We recommend paired tests per task, e.g. Wilcoxon signed-rank with an effect size.

---

## 5. Useful commands

```bash
.venv/bin/python harness/tc.py -h                                  # all commands
.venv/bin/python harness/tc.py prompt <task_id>                    # print the prompt
.venv/bin/python harness/tc.py eval   <task_id> <reply.md>         # correctness only (faster)
.venv/bin/python harness/tc.py bench  <task_id> <reply.md> --size L --min-time 2   # timing only
.venv/bin/python harness/tc.py run    <task_id> <reply.md> --sizes S,M,L --reps 5 --min-time 2
.venv/bin/python harness/tc.py check  <task_id>                    # verify a task (reference passes, stub fails)
```

`<reply.md>` can be a raw model reply or a plain `.py` file containing only the function.
`reference` evaluates the original human code.

---

## 6. Getting reliable measurements

- Use the **same machine and settings for all models and for the human baseline**, and run them in one session.
- Keep the machine quiet (no other heavy jobs), plugged in, and prevent sleep.
- For publication-grade numbers, use `--reps 10 --min-time 2`.
- Peak memory includes loading the inputs, which is the same for every implementation. Compare **ratios against the human code**, not absolute values.
- Runtime on macOS/Windows runs inside Docker's virtual machine. That's fine for comparisons on one machine, but report the platform.

---

## 7. Energy measurement (optional, Linux only)

Energy comes from the CPU's RAPL counters, which only bare-metal Linux on Intel/AMD exposes. Not virtual machines, WSL or macOS.

1. Check the machine: `sudo bash harness/check_machine.sh` must end with `RESULT: usable for energy measurement`.
2. Fix the CPU frequency and disable turbo/boost for stable results (commands are printed by the check script).
3. **Energy is not automated in this release.** Wrap the timing command with `perf`:

   ```bash
   sudo perf stat -a -e power/energy-pkg/,power/energy-ram/ -- \
     .venv/bin/python harness/tc.py bench <task_id> <reply.md> --size L --min-time 5
   ```

   Also measure an idle interval of the same length (`sudo perf stat -a -e power/energy-pkg/ -- sleep 5`) and subtract it. Divide by the number of passes reported by `bench` to get joules per pass.

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| `docker: command not found` / cannot connect | Start Docker Desktop or the Docker service. |
| `fetch_repos.py` reports `MISMATCH` | Delete `repos/<language>/<name>` and run it again. If it persists, GitHub changed the archive; please report it. |
| `StaleFileError` | Docker file sharing lagged for more than 10 s. Rerun. On macOS, make sure the project folder is shared with Docker. |
| Many `crashed` results | Increase Docker's memory to ≥ 6 GB (Docker Desktop → Settings → Resources). |
| `tcmeasure: Exec format error` | The helper was built for another CPU. Rerun step 3 of `setup.sh`. |
| `requests` tasks are slow | Its full test suite takes about 2 minutes per evaluation. This is expected. |
| Want to start fresh | Delete `.work/` and rerun `setup.sh` (step 5 recreates working copies). |

---

## 9. Rules for fair use

- Send the prompt **unchanged**. Never give the model `reference.py`, the tests or the benchmark files.
- Don't edit the tasks. Results are only comparable on the released tasks.
- Report: the model version, the date, the decoding settings, the number of samples, the retry policy, the platform and the harness options (`--reps`, `--min-time`).
- **Contamination:** these libraries are public, and probably in the training data of current models. Report the results with that in mind. Comparing a model's answer with `reference.py` (e.g. edit distance) helps detect memorisation.

---

## 10. Licences and citation

Each task contains code from its library, under that library's licence (see `index.csv` → `license`, and each
library's `LICENSE` file in `repos/`). The specifications, harness and benchmark data are released by the authors
(licence and citation: see the paper).
