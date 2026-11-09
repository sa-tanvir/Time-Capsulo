Workload: seeded `[Type, Raw, Str, Num, stop]` Results; mostly random JSON objects/arrays (`json.dumps` with
compact / spaced / indented style, ASCII-escaped or raw UTF-8, nested containers, escaped strings, numbers,
literals), 20% with leading whitespace, 15% with an early stop (iterator returns false at call `stop`).
S adds scalar Results and malformed/edge documents. Approx. bytes per document: ~150 (S), ~1.5 KB (M), ~15 KB (L).
The driver is a Go test in package `gjson`; it calls `r.ForEach(fn)` and hashes every (key, value) pair (all fields).
