Workload: seeded GJSON paths built from names (with `\.`/`\|` escapes, wildcards, `@modifiers`), `#`, and
`#(...)`/`#[...]` queries (nested sub-queries, quoted values containing `|`, brackets and escaped quotes);
40% end with a top-level `|name`, 10% are `{...}` multipaths, rare inner pipes. S adds hand-written edge cases.
Components per path: 1-4 (S), 25-40 (M), 250-400 (L) (~17 / 210 / 2000 bytes).
The driver is a Go test (`TestTCBench`) copied into package `gjson`; it calls `splitPossiblePipe(p)` directly.
