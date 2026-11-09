# Time Capsulo: Quickstart

Time Capsulo has 260 tasks. Each task is one real function from a 2018–2019 open-source library (Python, Go, JavaScript, Rust, Java, C++). A model writes the function from a specification, and the harness puts the code back into the original library and judges it by the library's own tests and by an output check. Correct code is then timed.

You can use the benchmark at two levels.

## Level 1: only read the tasks (no installation)

Everything a model needs is in plain files:

- `tasks.jsonl`: one JSON object per task, with the `prompt` to send to your model and the task's metadata (see `DATA_FORMAT.md`).
- `benchmark/tasks/<task_id>/prompt.md`: the same prompt as a file.
- `index.csv`: one row per task (library, version, commit, function, size, complexity, number of covering tests).

```python
import json
tasks = [json.loads(line) for line in open("tasks.jsonl")]
print(len(tasks), tasks[0]["task_id"])
reply = my_model(tasks[0]["prompt"])      # send the prompt unchanged
open(f"replies/MyModel/{tasks[0]['task_id']}.md", "w").write(reply)
```

Send each prompt **unchanged**, and save the raw reply (explanations are fine; the harness extracts the code block).

## Level 2: score the replies (needs Docker)

Requirements: Docker running (≥ 4 GB RAM for Docker, ≥ 15 GB free disk), Python ≥ 3.8, internet for the one-time setup, and a Unix shell (Linux or macOS; the published verification ran on Apple-silicon macOS with Docker Desktop; x86-64 Linux is expected to work but was not part of our tests; on Windows use WSL2, untested).

```bash
./setup.sh                 # all six languages, about 45–90 minutes, one time
# or only some languages:  ./setup.sh python go

# 1. self-test: the original code passes, an empty stub fails
.venv/bin/python harness/tc.py check python__more-itertools__more_itertools_more__windowed

# 2. the human baseline for a task, and your model's answer for the same task
.venv/bin/python harness/tc.py run <task_id> reference --label human --out results.jsonl
.venv/bin/python harness/tc.py run <task_id> replies/MyModel/<task_id>.md --label MyModel --out results.jsonl

# 3. the results table (pass rate, outcome labels, runtime/memory ratio vs the human code)
.venv/bin/python harness/summarize.py results.jsonl
```

To run every task, loop over `ls benchmark/tasks` (see `USER_GUIDE.md`, section 4). A full run of the 260 human baselines takes several hours on a laptop, so run the languages you need first.

## Where to read more

| File | Content |
|---|---|
| `USER_GUIDE.md` | the full procedure: protocol, outcome labels, reliable timing, energy, troubleshooting, rules for fair use |
| `DATA_FORMAT.md` | every file and field in the dataset and in the result records |
| `README.md` | what the benchmark contains, the checks it passed, notes on each language and on limitations |
| `NOTICE.md`, `LICENSE`, `CITATION.cff` | licences of the 30 libraries, licence of this dataset, how to cite |
| `CHECKSUMS.sha256` | checksum of every file in this folder |
