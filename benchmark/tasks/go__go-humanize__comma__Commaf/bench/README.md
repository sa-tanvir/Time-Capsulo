Workload: seeded finite float64 values (JSON numbers written with Python repr, which round-trips
exactly), 6k per size, 40% negative, 30% with negative exponents (long fractions). Magnitude
exponent is 0-6 (S, plus fixed edge cases incl. -0, MaxFloat64, SmallestNonzeroFloat64),
10-40 (M) and 100-300 (L), so output length grows per size. The driver is a Go test
(`TestTCBench`) copied into package `humanize`; it calls `Commaf(v)` directly and hashes the
quoted results (check) or times the calls (time).
