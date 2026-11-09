# C++ blind test (2026-10-21)

50 fresh agents-as-solvers (5 agents, one per library) read only `prompt.md` and answered each task; answers were scored with the full pipeline (`tc.py run`).

- Round 1: 48/50 passed (`results.jsonl`).
- Failures, both spec gaps, fixed and re-tested with fresh agents (`results_rerun.jsonl`, both passed):
  - `cpp__json ... diff` (compile_error): the context said `detail::json_pointer<basic_json>`, but the class is `nlohmann::json_pointer` (not in `detail`). Context corrected.
  - `cpp__fmt ... format_float` (timeout): the context documented fmt's internal digit generators (`fixed_handler`, `grisu_shortest_handler`, `fallback_format`, `fp` boundary members) only partially and inconsistently. Those internals are now marked undocumented, and the spec asks for the result only.
- Contamination note: the json solver reported that it wrote most answers from memory of nlohmann/json 3.7.2 (the prompts name the library). This applies to every library in the benchmark.
- Replies: `replies/` (`*.round1-failed.md` = the failed round-1 answers); per-library ambiguity notes: `_notes_*.md`.
