Workload: replacement-text fragments starting (mostly) with `$`. S holds the literal cases from the unit and
replace/expand tests plus edge cases (empty, lone `$`, unclosed/empty braces, u32 overflow, leading zeros,
non-ASCII after the name) and short random references; M/L hold references with 60-200 / 600-2000 character
names (alphanumeric/underscore or all-digit, braced or bare, with assorted trailing text). Each line is hex-encoded bytes.
Invocation: `driver.rs` is appended to `src/expand.rs` of a container-local copy (`/tmp/w`, `/w` untouched) as
`mod tc_bench` and run with `cargo test --release`; it calls `find_cap_ref(&[u8])`. `check` hashes the variant, name/number and end offset (FNV-1a 64).
