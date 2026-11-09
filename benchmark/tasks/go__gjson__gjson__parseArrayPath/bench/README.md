Workload: seeded remaining-paths at an array: plain first components (some containing `#`), `#.key`, bare `#`,
and `#(...)`/`#[...]` queries (nested sub-queries, quoted values with `.`, `|`, brackets, escaped quotes; 5%
unbalanced), optionally followed by `#`, then `.rest`/`|rest` or nothing. S adds hand-written edge cases.
First-component length: 1-12 chars (S), 100-250 (M), 1000-2500 (L).
The driver is a Go test (`TestTCBench`) copied into package `gjson`; it calls `parseArrayPath(p)` and hashes every field.
