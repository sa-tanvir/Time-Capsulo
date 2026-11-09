Workload: seeded fixed-point decimal strings (optional '-', integer part, '.', fraction ending
in a run of zeros of random length). 6k strings per size. S: fractions up to 12 digits plus fixed
edge cases (FormatFloat-style "x.000000", "-0.000000", "7."); M: up to 120 fractional
digits; L: up to 1,200 fractional digits. The driver is a Go test (`TestTCBench`)
copied into the `humanize` package; it calls `stripTrailingZeros(s)` directly and hashes the
quoted results (check mode) or times the calls (time mode).
