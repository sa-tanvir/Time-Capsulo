Workload: seeded pairs of pre-release strings. S starts with the test-suite pairs and edge
cases (empty strings, uint64 overflow, negative-looking identifiers), then random pairs.
Pairs are usually related (identical, one identifier changed, prefix, extension) so the
comparison has to walk shared identifiers. Identifiers per string: 1-3 (S), 4-12 (M), 26-80 (L).
The driver is a Go test (`TestTCBench`) copied into the `semver` package; it calls
`comparePrerelease(a, b)` directly and hashes the results (check) or times the calls (time).
