Workload: pairs of strings. S holds the literal edge cases from the test suite (empty, multibyte, unequal length,
transpositions) plus short random pairs; M/L hold longer pairs that `driver.rs` expands deterministically
(splitmix64) from `G` lines: random text over 2-64 symbol alphabets (ASCII and multibyte) and a copy with 0-50% edits.
Invocation: `driver.rs` is appended to `src/lib.rs` of a container-local copy of the workspace (`/tmp/w`, so `/w` is never modified) as `mod tc_bench` and run with `cargo test --release`; it calls
`osa_distance(&str, &str)`. Inputs are prepared before timing; `check` hashes all outputs with FNV-1a 64.
