Workload: seeded (n, b, maxmag) triples; n is a decimal string, b is 10/1000/1024/2/16 or random
in [2, 10^6], maxmag is -1/0 (no cap) in 40% of cases, otherwise a cap chosen so the final
quotient fits in int64. n has 1-30 digits (S, 6k cases + test-derived edge cases), 30-300 (M,
1.5k) and 300-3,000 (L, 200). The driver is a Go test (`TestTCBench`) copied into package
`humanize`; n is re-copied from a pristine big.Int before every pass (untimed) because oomm
overwrites it. Check mode hashes (FormatFloat 'g' -1 of the value, mag).
