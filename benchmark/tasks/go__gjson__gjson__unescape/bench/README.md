Workload: seeded JSON string bodies (text between the quotes, from `json.dumps`, ASCII-escaped or raw UTF-8)
with simple escapes, `\uXXXX`, surrogate pairs, plus injected oddities (lone/reversed surrogates, invalid hex)
in 30% of cases and a decoding stopper (unknown escape, raw control byte, truncated `\u`) in 5%.
S adds hand-written edge cases. Body length: 0-40 chars (S), 300-600 (M), 3000-6000 (L).
The driver is a Go test (`TestTCBench`) copied into package `gjson`; it calls `unescape(s)` directly.
