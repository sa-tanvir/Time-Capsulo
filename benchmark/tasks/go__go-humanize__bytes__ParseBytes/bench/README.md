Workload: seeded size strings, 6k per size: integer part (sometimes comma-grouped, sized to stay
below 2^64 bytes except ~10% overflow cases), optional fraction, optional white space, unit in
random case (all 26 table units, ~7% unknown units), optional trailing space. Fraction length is
0-8 (S, plus all test inputs and error edge cases), 0-80 (M) and 0-800 digits (L). The driver is
a Go test (`TestTCBench`) copied into package `humanize`; it calls `ParseBytes` directly and
hashes the value or "ERR" (check) or times the calls (time).
