Workload: seeded multipaths `[...]`/`{...}` whose elements are plain paths, `name:path`, `"quoted name":path`,
nested multipaths, paths with `#(...)` queries holding quoted `,`/`:`/`}`, escaped `\,` `\:` `\]`, and
`|@modifier` suffixes; followed by a remainder (`|@ugly`, `.@pretty`, ...); 5% are never closed.
S adds hand-written edge cases. Elements per multipath: 1-4 (S), 20-40 (M), 200-400 (L).
The driver is a Go test (`TestTCBench`) copied into package `gjson`; it calls `parseSubSelectors(p)` directly.
