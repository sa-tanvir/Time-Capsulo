Workload: seeded inputs that start with a JSON string literal (from `json.dumps`, ASCII-escaped or raw UTF-8),
some needing no escapes and some with `\"`, `\\`, control escapes, `\uXXXX` and surrogate pairs; followed by
trailing document text, or ending at the closing quote (10%), or unterminated (5%). S adds hand-written edge cases.
Content length: 0-40 chars (S), 300-600 (M), 3000-6000 (L).
The driver is a Go test (`TestTCBench`) copied into package `gjson`; it calls `tostr(s)` directly.
