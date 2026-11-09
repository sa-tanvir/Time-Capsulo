# Time Capsulo: a benchmark of pre-AI human code vs AI-generated code (Python, Go, JavaScript, Rust, Java, C++)

Version 1.0 (October 2026). Time Capsulo measures whether code written by AI models is as correct as, and
more or less efficient than, code that humans wrote before AI coding assistants existed.

**Start here:** `QUICKSTART.md` (use the tasks in 5 minutes, or score a model's answers), `DATA_FORMAT.md` (every file and field), `USER_GUIDE.md` (the full procedure). `tasks.jsonl` holds all 260 prompts in one file.


**260 tasks from 30 repositories released in 2018–2019, in six languages.** Each task is one real function, re-implemented by a model from a specification and judged inside its original library.

| Language | Repository | Version | Release date | Tasks |
|---|---|---|---|---|
| Python | more-itertools | v7.2.0 | 2019-07-20 | 10 |
| Python | click | 7.0 | 2018-09-26 | 10 |
| Python | sortedcontainers | v2.1.0 | 2018-11-22 | 10 |
| Python | dateutil | 2.8.1 | 2019-11-03 | 10 |
| Python | requests | v2.22.0 | 2019-05-16 | 10 |
| Go | go-humanize | v1.0.0 | 2018-07-13 | 8 |
| Go | semver (Masterminds) | v3.0.3 | 2019-12-13 | 3 |
| Go | mux (gorilla) | v1.7.0 | 2019-01-25 | 9 |
| Go | gjson | v1.3.5 | 2019-11-18 | 9 |
| Go | cobra | v0.0.5 | 2019-06-07 | 9 |
| JavaScript | qs | v6.9.1 | 2019-11-08 | 4 |
| JavaScript | node-semver | v6.3.0 | 2019-07-24 | 10 |
| JavaScript | validator.js | 12.1.0 | 2019-11-21 | 6 |
| JavaScript | lodash | 4.17.14 | 2019-07-10 | 10 |
| JavaScript | moment | 2.24.0 | 2019-01-22 | 10 |
| Rust | strsim-rs | 0.9.2 | 2019-05-09 | 5 |
| Rust | textwrap | 0.11.0 | 2018-12-10 | 3 |
| Rust | rust-base64 | v0.11.0 | 2019-10-25 | 4 |
| Rust | clap | v2.30.0 | 2018-02-14 | 10 |
| Rust | regex | 1.0.0 | 2018-05-02 | 10 |
| Java | commons-codec | 1.13 | 2019-07-22 | 10 |
| Java | commons-text | 1.8 | 2019-08-31 | 10 |
| Java | jsoup | 1.12.1 | 2019-05-13 | 10 |
| Java | commons-lang | 3.9 | 2019-04-11 | 10 |
| Java | gson | 2.8.6 | 2019-10-05 | 10 |
| C++ | pugixml | v1.10 | 2019-09-12 | 10 |
| C++ | fmt | 6.1.0 | 2019-12-02 | 10 |
| C++ | double-conversion | v3.1.5 | 2019-05-26 | 10 |
| C++ | spdlog | v1.3.1 | 2019-01-18 | 10 |
| C++ | nlohmann/json | v3.7.2 | 2019-11-11 | 10 |
| | | | **Total** | **260** |

`index.csv` has one row per task: commit SHA, licence, file, function, lines of code, complexity, number of covering tests, and spec-leakage score. `repos.csv` pins each source by tag, commit and content hash. `benchmark/selection_logs/` lists every function that was skipped, added or retired during selection, with the reason.

## Verification (all passed)

| Check | Python | Go | JavaScript | Rust | Java | C++ |
|---|---|---|---|---|---|---|
| Selection rule: ≥ 8 lines of logic, complexity ≥ 3, contains a loop or recursion (comments and strings ignored), deterministic, ≥ 2 covering tests | 50/50 | 38/38 | 40/40 | 32/32 | 50/50 | 50/50 |
| Full check with the final harness: the original code passes every stable test of its repo (Python 3.7 / Go 1.13 / Node.js 10 / Rust 1.40 / Java 8 / GCC 9.4 with CMake 3.16, the libraries' own 2018–2019 test suites) and reproduces its recorded outputs on all workloads; a stub fails the covering tests; the spec shares < 12 consecutive code tokens with the original | **50/50** | **38/38** | **40/40** | **32/32** | **50/50** | **50/50** |
| Blind check: a fresh model that saw only `prompt.md` (never the original code) implemented each function, and the implementation passed the repo's tests and the output check | **50/50** | **38/38** | **40/40** | **32/32** | **50/50** | **50/50** |

Blind-check evidence is in `benchmark/blind_check/`. 11 Go and 12 JavaScript specs were clarified after the first blind run. They were re-tested on their final wording (`*.rerun-2026-10-18.md`, `rerun_go_2026-10-18.jsonl`, `rerun_js_2026-10-18.jsonl`). The Rust answers and results are in `blind_check/replies/rust__*.md` and `blind_check/rust_results.jsonl`; all 32 passed on the first complete pass of the final specs. Java: 47 of 50 passed the first blind round; the 3 failures were spec gaps (`NumberUtils.createNumber`, `WordUtils.wrap`, `StringsComparator.getMiddleSnake`). The specs were extended and re-tested with fresh blind agents; `wrap` and `getMiddleSnake` passed after one fix, `createNumber` after two. The answers that failed are kept as `*.round1-failed.md` / `*.round2-failed.md`; results are in `blind_check/java_results.jsonl` (round 1) and `java_rerun_results.jsonl` (re-tests).

C++: 48 of 50 passed the first blind round (`blind_check/cpp_results.jsonl`, `cpp_README.md`, `cpp_notes/`). The 2 failures were spec gaps: json `diff` (the context named the wrong namespace for `json_pointer`) and fmt `format_float` (the context described fmt's internal digit generators only partly). Both specs were fixed and re-tested with fresh blind agents, and both passed (`cpp_rerun_results.jsonl`). The json solver reported that it wrote most answers from memory of the library (see contamination below).

## Contents of each task folder

| File | Content | Given to the model |
|---|---|---|
| `prompt.md` | the exact prompt (spec, context and stub assembled) | **yes, this is what is sent** |
| `spec.md`, `stub.<ext>`, `context.md` | specification, signature, file context | yes (inside the prompt) |
| `reference.<ext>` | the original 2018–2019 human implementation | no (hidden) |
| `task.json` | provenance, metrics, covering tests, benchmark commands | no |
| `bench/` | seeded workload generator (S/M/L), driver, `expected.json` (reference output fingerprints) | no |

`<ext>` is `py`, `go`, `js`, `rs`, `java` or `cpp`. Workload files are regenerated deterministically from `bench/gen_workload.py`.

## Evaluating a model

**Full setup and usage instructions: see `USER_GUIDE.md`** (`./setup.sh`, then `tc.py run`). In short:

```
.venv/bin/python harness/tc.py run <task_id> <model_reply.md> --label <model> --out results.jsonl
.venv/bin/python harness/tc.py run <task_id> reference  --label human --out results.jsonl
.venv/bin/python harness/summarize.py results.jsonl
```

Correctness is checked first:
1. interface/format check;
2. the original tests;
3. output checks on the S, M and L workloads.

Only correct code is then measured, with calibrated runtime and peak memory. Each reply receives exactly one label: `passed`, `failed_tests`, `wrong_output`, `compile_error`, `timeout`, `crashed`, `interface_violation`, `format_violation` or `no_code`.

## Notes on the methodology

**General**
- Specifications were written with the help of an LLM and verified automatically (leakage check, blind check); `spec_status` is `checked-v1.0`.
- Method tasks list the object's internal fields in `context.md` ("Instance state"), which models need in order to write a method body.
- Energy measurement (RAPL) requires a bare-metal Linux machine (Intel/AMD). Runtime and memory work on any Docker host.
- Outcome labels: a compile or syntax error is not always reported as `compile_error`. In our check it was for Java (all 5 libraries), Rust (strsim-rs, regex, clap), JavaScript (qs, lodash, moment) and Go (gjson); Python catches syntax errors before any test runs. In Go cobra (a build error in one package leaves the other packages' tests running), JavaScript node-semver and validator.js (a syntax error makes all tests fail), such an answer was labelled `failed_tests`. The other libraries were not tested separately. Whether an answer passes or fails is never affected: after a reference run, we evaluated one deliberately uncompilable answer in each of those libraries, and none was reported as `passed`.
- Training-data contamination: all libraries are public. Commons-text was split out of commons-lang, and a few functions are related: `WordUtils.wrap` (about 77% of lines equal across the two libraries), `StrSubstitutor`/`StringSubstitutor.substitute` (about 63%). A function that was 100% identical in both (`NumericEntityUnescaper.translate`) is kept only in commons-text.
- C++ solvers also know these libraries well (the json solver said it recalled nlohmann/json 3.7.2 from memory); results on public, well-known libraries should be read with contamination in mind.
- Base images are pinned by digest (`harness/docker/*.Dockerfile`, and the `alpine` helper image in `setup.sh`). We verified that each digest is the exact base of the images used for the published results.

**Python**
- requests: its 2019 test suite needs pytest 3.10.1, and Brotli 1.0.9 (2020) replaces brotlipy, which has no ARM build. Both are test-only dependencies.
- dateutil: the `_parse` driver fixes the two-digit-year window to 2019, and the rrule tasks use fixed timezone tables, so results don't depend on today's date or the host.
- 5 tasks selected under an earlier, buggy loop filter were replaced by the next-ranked qualifying functions.

**Go**
- Toolchain: Go 1.13 (September 2019). Tests run offline. cobra and gjson download the dependency versions pinned by their own 2019 `go.mod`/`go.sum` (e.g. pflag v1.0.3, tidwall/match v1.0.1) once during setup. go-humanize v1.0.0 predates Go modules, so setup runs `go mod init` in the working copy only.
- After injection, a pinned `goimports` (x/tools, release-branch.go1.13) fixes the import list, for the human code and every model alike. So a missing or unused import is never a failure in itself. Some functions use a package that, in the original file, only they import.
- Each top-level Go test runs in its own process (`go-test-each`), so a panicking answer only fails the tests that reach it.
- Fewer than 10 tasks per repository: go-humanize has only 8 eligible functions. 10 Go tasks (semver 7, mux 1, gjson 1, cobra 1) were retired because they failed the corrected loop/recursion rule. They were not replaced.

**JavaScript**
- Toolchain: Node.js 10 LTS + npm 6. Only the devDependencies the tests need are installed, with each version range resolved **as of the library's release date** (`npm --before=<date>`, see `harness/docker/javascript/npm-install-isolated.sh`). Lint, coverage and bundling tools are omitted.
- Small adapters (`harness/docker/javascript/`) make each test runner (tape, tap, mocha, QUnit) report one result per test.
- moment: `grunt transpile-raw` is replaced by an equivalent rollup 0.67 build (`moment-build.js`, same UMD output), so that injected source changes are tested. The core unit tests run, the locale-data tests are skipped, the time zone is UTC, and the benchmark drivers fix `moment.now` to 2019-01-21.
- lodash: the main QUnit suite runs against `lodash.js`. Module-private helpers (e.g. `baseClone`) are benchmarked through their public wrappers (e.g. `_.cloneDeep`).
- validator.js: the mocha suite runs on `src/` through `@babel/register`.
- Fewer than 10 tasks per repository: qs has only 4 eligible functions (functions on the parse side break more than half of its suite when stubbed). 4 validator.js tasks were retired because they failed the corrected loop/recursion rule. They were not replaced.

**Rust**
- Toolchain: Rust 1.40.0 (December 2019), `cargo test --lib --tests` (doc-tests are not run, because the harness's result parser cannot read their names). Tests run with default features only.
- Dependencies: Cargo cannot resolve "as of a date", so the **exact dependency versions are fixed by shipped lockfiles** (`benchmark/lockfiles/`). `tc.py setup` copies the lockfile into the working copy and runs `cargo fetch --locked`. These are the same versions the baselines were made with. Many crates in these lockfiles were pinned back to early-2018 to late-2019 versions, because the newest ones do not compile on Rust 1.40. `setup_cmd_generate` in each repo config records the commands that produced the lockfiles. One exception is `url` 1.7.2 (November 2018) for clap, because older versions do not compile on Rust 1.40.
- Bench drivers are appended to the library source in a container-local copy (`/tmp/w`) and built with `--release`; the library working copy is never modified. Build time is not part of the measured run.
- clap: the 4 tests in its `version` module print the version text without a trailing newline directly to stdout. The text lands on a random test-result line, so the harness cannot match that test's name. The tests always pass; the module is excluded (`flaky` in the baseline). 6 of clap's 10 tasks come from `src/app/help.rs`, more than the usual limit of 4 per file, because the other eligible functions were parser internals that cannot be specified in isolation.
- clap: its help workloads keep wrap widths at 28 columns or more, because its old `textwrap` 0.9 dependency panics on multi-byte text at narrower widths.
- regex: 6 engine-internal state-machine functions (the DFA, PikeVM and backtracking search loops) were skipped, because they operate on the matcher's internal state and cannot be specified or benchmarked on their own. 5 other functions were added in their place (logged with reasons in `benchmark/selection_logs/selection_overrides_rust.csv`). The regex setup removes the auxiliary workspace crates from `Cargo.toml` in the working copy only, and makes dependency constraints exact.
- 3 libraries (strsim-rs, textwrap, rust-base64) have 3–5 tasks because only that many functions were eligible.
- Private functions are benchmarked by a small test module that the driver appends to the file, inside the container-local copy.

**Java**
- Toolchain: Maven 3.6.3 on Amazon Corretto 8 (an OpenJDK 8 build, 8u282; the usual OpenJDK 8 Maven image has no ARM build), pinned by digest. Maven downloads each library's dependencies and plugins once, during setup, into the Docker volume `tc-cache-m2`; tests then run offline (`mvn -o`) with the quality plugins (checkstyle, rat, jacoco, javadoc, spotbugs and similar) skipped. Dependency versions are those in each library's own `pom.xml`; transitive and plugin versions come from the poms and Maven 3.6's defaults, so setup relies on Maven Central still serving them.
- Baselines (stable tests): commons-codec 939 (of 973 run; 34 skipped), commons-text 989 (18 tests excluded: DNS, local-host and URL lookups), jsoup 677 (1 failing at baseline, `ConnectTest::multiCookieSet`, and 10 `@Ignore`d), commons-lang 4,595 (4 skipped) and gson 1,050 (1 skipped). No flaky tests were found.
- gson: the library's `pom.xml` needs JDK 9 for `module-info.java`, which the JDK 8 image cannot compile. The setup therefore compiles the main classes with `javac -source 1.7 -target 1.7` (without `module-info.java`; the build-config class is generated from its template), the sources being untouched. The build deletes its old classes first and stops on a compile error.
- The bench drivers call private methods through reflection in 18 of the 50 tasks (commons-text 7, gson 5, commons-lang 4, jsoup 2). This adds the same fixed overhead to the human code and to every model's code.
- Reference passes at the largest workload size take between 7 ms (jsoup `looksLikeUtf8`) and 1.1 s (commons-lang `replaceEach`), with medians of 31 ms (jsoup) to 190 ms (gson). Short passes are repeated by the timing calibration, but energy per pass will be noisy for the shortest ones.
- Several tasks have only 2 covering tests; for them the output check does most of the work. Some specs have to describe exact tie-breaking or boundary rules (for example `StringsComparator.getMiddleSnake`, `NumberUtils.createNumber`) and are therefore close to the algorithm; the human spec review should read them with care.
- Some functions are only reachable indirectly: `HttpConnection.looksLikeUtf8` is covered only through the HTTP header setters; the private `DaitchMokotoffSoundex.soundex` is driven through the public `soundex`/`encode`; `LinkedTreeMap.rebalance` and `LinkedHashTreeMap.rebalance` are driven through `put`/`remove`. See each task's `bench/README.md`.

**C++**
- Toolchain: Ubuntu 20.04 (pinned by digest) with GCC 9.4.0, CMake 3.16.3 and make 4.2.1 (the `g++-9`, `cmake` and `make` packages come from the Ubuntu 20.04 archive at image-build time, so a rebuilt image may carry a later 9.4.0 package revision). Library tests are built with `-O1` and no debug info; benchmark drivers are built with `-O2 -std=c++11`.
- Build output lives in a Docker volume per library (`tc-build-<name>`). The harness restores sources with their original mtimes, so `tc-sync-mtimes` (in the image) touches the files whose content changed, to keep incremental builds correct. Every build deletes the old test binaries first and requires all of them to build, so a compile error is never hidden by a stale binary (found and fixed on fmt: one header-only test binary survived a header error).
- Baselines (stable tests): pugixml 880, fmt 339 (4 failing at baseline), double-conversion 79, spdlog 93, nlohmann/json 84 doctest test cases in 42 binaries. No flaky tests were found. Cold builds can be slow (the very first double-conversion baseline took 15 minutes on a loaded machine; in a clean-copy test, setup plus the first `check` of one task per library took 12 s to about 2 minutes each); a `check` takes 8 s (pugixml, double-conversion) to 3 min (json, fmt), because header changes recompile every test binary.
- Drivers `#include` the library's `.cpp`/headers and compile into a content-hash-keyed cache in the build volume, so `/w` is never written. spdlog drivers use `-fno-access-control` to reach private members, and the tests (and so the drivers and specs) define `SPDLOG_ENABLE_MESSAGE_COUNTER`. double-conversion drivers are built with `-DNDEBUG`, while its own tests keep asserts on.
- pugixml: 8 of the 10 scanner picks (XPath evaluator/parser internals, `parse_exclamation`, `node_output`) could not be isolated and were replaced by self-contained functions (logged in `benchmark/selection_logs/selection_overrides_cpp.csv`). spdlog: the scanner found only 3 eligible candidates, all skipped (live sinks, file I/O, threads); the 10 tasks were sampled by hand from pure formatting helpers, three of them exercised by 56–58 of the 93 tests. fmt: the `format_float` digest is canonicalised in the driver, and workloads avoid known fmt 6.1.0 quirks (garbage digits beyond 17 in fixed notation, `%e` of 0.0).
- json: the tests are built against the split headers (`-DJSON_MultipleHeaders=ON`), not the amalgamated `single_include`, so stubs act on the files the tests compile. The reader drivers use a recording SAX handler that throws on parse errors.
- Some specs mark inputs as out of contract (for example subnormal results of double-conversion `RadixStringToIeee`, `RoundWeed` inputs with a small unsafe interval); the workloads stay inside the contract.
- Timing: pugixml `sort` takes about 4 s for the largest workload on the reference. Short passes are repeated by the timing calibration, but energy per pass may be noisy for the shortest ones.
- Linux-only build (the C++ toolchain image is Linux; spdlog tests use POSIX file operations).

## Intended use and limitations

- Intended use: compare the correctness and efficiency (runtime, memory, and energy where measured) of code written by AI models against the human code that existed in 2018–2019, on function-level tasks inside real libraries.
- The specifications were written with the help of an LLM and checked automatically (leakage check, blind check); `spec_status` is `checked-v1.0`.
- The libraries are public and very well known, so a model may have seen them in training. Treat results with this contamination risk in mind.
- Tasks are single functions, not whole programs. A task needs the library's tests, so the answer is judged only as far as those tests and the output check reach.
- Energy needs a bare-metal Linux machine with RAPL; runtime and memory work on any Docker host. Memory is measured at the level of the whole benchmark process (peak RSS), so small differences between answers are within noise.
- Published verification ran on Apple-silicon macOS with Docker Desktop. Linux x86-64 is expected to work but was not tested.

## Licence and citation

- Code taken from the 30 libraries (`reference.*`, excerpts in `context.md`, stubs) stays under each library's own
  licence. All are permissive (MIT, BSD-3-Clause, ISC, Apache-2.0). Licence texts are in `third_party_licenses/`;
  versions, commits and a statement of changes are in `NOTICE.md`.
- Code written for Time Capsulo (harness, `setup.sh`, benchmark drivers and workload generators) is under the MIT License.
- Data and documentation written for Time Capsulo (specifications, prompts, metadata, expected digests,
  blind-check evidence, guides) are under CC BY 4.0. See `LICENSE` for the exact scope and
  `LICENSE-DATA-CC-BY-4.0.txt` for the full text.
- The specifications were written with the help of a large language model and checked automatically (leakage check, blind check).
- If you use the benchmark, please cite it as described in `CITATION.cff`.
