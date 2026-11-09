Workload: seeded decimal integers stored as JSON strings, 40% negative, ~15% ending in long runs
of zeros. S = 6k values of 1-20 digits plus fixed edge cases from the tests (0, +-10^k, 2^64,
the 44-digit test value); M = 2k values of 20-200 digits; L = 600 values of 200-2,000 digits.
The driver is a Go test (`TestTCBench`) copied into package `humanize`. BigComma may modify its
argument, so inputs are re-copied from pristine big.Ints before every pass, outside the timed
region; it hashes the quoted results (check) or times only the BigComma calls (time).
