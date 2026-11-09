Workload: seeded size strings, 6k per size: integer part (sometimes comma-grouped), optional
fraction, optional white space, unit in random case (all 34 table units up to YiB, ~7% unknown
units), optional trailing space. Integer/fraction lengths are up to 4/8 digits (S, plus all test
inputs and error edge cases), 40/80 (M) and 400/800 (L), parsed exactly. The driver is a Go
test (`TestTCBench`) copied into package `humanize`; it calls `ParseBigBytes` directly and
hashes the decimal result or "ERR" (check) or times the calls (time).
