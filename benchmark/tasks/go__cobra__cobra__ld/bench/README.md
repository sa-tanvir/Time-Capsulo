Workload: seeded string pairs `[s, t, ignoreCase]`. S = 3000 short pairs (0-12 bytes) plus fixed
edge cases (empty strings, case differences, multi-byte UTF-8, the suggestion examples from the tests);
M = 300 pairs of 40-120 bytes; L = 40 pairs of 400-1200 bytes. 60% of pairs are mutations of each other.
The driver is a Go test (`TestTCBench`) copied into package `cobra`; it calls `ld(s, t, ic)` directly
and hashes the distances (check) or times the calls (time).
