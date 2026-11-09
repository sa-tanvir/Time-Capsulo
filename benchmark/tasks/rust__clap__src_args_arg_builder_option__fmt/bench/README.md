Workload: one option argument per line (name, long, short, Multiple/RequireEquals/RequireDelimiter flags, delimiter,
num_vals, value names). S holds the edge cases from the unit/help tests plus small random options; M/L hold options with
30-1200 and 3000-12000 values (long lists are expanded by the driver from `#count:seed`) (value names or a value count), so the rendered string grows ~10x per size.
Invocation: `driver.rs` is appended to `src/args/arg_builder/option.rs` of a container-local copy (`/tmp/w`, `/w` is never
modified) as `mod tc_bench`; it builds `OptBuilder` values before timing and calls `format!("{}", opt)`, i.e. the target
`Display::fmt`. `check` hashes all rendered strings with FNV-1a 64. Run with `cargo test --release`.
