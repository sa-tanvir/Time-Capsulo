Workload: seeded GJSON queries `#(...)`/`#[...]` with dotted left paths (escaped `\(` `\=`, wildcards), nested
sub-queries (up to 3 levels), random whitespace, all operators and values (quoted strings with brackets,
escaped quotes and backslashes, integers, literals), 15% existence-only; followed by a remainder (`.last`, `#|#`, ...).
~4% truncated (unbalanced) and ~2% not starting with `#(`. S adds hand-written edge cases.
Left path / value length: 1-12 chars (S), 100-250 (M), 1000-2500 (L). Driver: Go test in package `gjson` calling `parseQuery(q)`.
