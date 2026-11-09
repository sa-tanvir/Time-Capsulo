Workload: seeded inputs that start with a JSON object/array, a `(...)` group or a JSON string literal,
followed by trailing text (`,`, `]`, `|@reverse`, ...). Values contain nested containers, escaped quotes,
backslashes and brackets inside strings; ~5% are unterminated containers. S adds hand-written edge cases.
Approx. bytes per case: ~120 (S), ~1.5 KB (M), ~17 KB (L), depth up to 2/3/5.
The driver is a Go test (`TestTCBench`) copied into package `gjson`; it calls `squash(s)` directly.
