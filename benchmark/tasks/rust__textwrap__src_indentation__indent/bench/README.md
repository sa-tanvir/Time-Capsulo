Workload: multi-line text blocks (S: literal cases from the tests/docs plus short random blocks; M: 60-200 lines;
L: 600-2000 lines per case) with indents mixing spaces, tabs, NBSP and U+3000, blank and whitespace-only lines,
CRLF endings and optional final newline. Strings are stored escaped, one case per line.
Invocation: `driver.rs` is appended to `src/indentation.rs` of a container-local copy (`/tmp/w`, `/w` untouched) as
`mod tc_bench` and run with `cargo test --release`; it calls `indent(..)` directly. Inputs are parsed before timing;
`check` hashes all outputs with FNV-1a 64.
