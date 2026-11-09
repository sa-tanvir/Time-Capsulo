Workload: seeded int64 values (stored as JSON strings): fixed edge cases (0, +-999/1000,
internal-zero groups, MaxInt64, MinInt64) followed by random values with 1-19 digits,
40% negative. S = 20k values; M/L = 50k values passed 2x/20x per pass ("inner").
The driver is a Go test (`TestTCBench`) copied into the `humanize` package. It calls
`Comma(v)` directly and hashes the quoted results (check mode) or times the calls (time mode).
