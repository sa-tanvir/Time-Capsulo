Workload: one option argument per line: Hide{Env,Default,PossibleValues} settings, the writer's global hide-possible-values
switch, env var (name only or name=value), default value, visible/hidden aliases and possible values. S holds the
help-test cases (env shown/hidden, defaults, aliases, possible values, all combined) plus small random options; M/L hold
300-3000 and 3000-30000 aliases/possible values per option (expanded by the driver from `#count:seed`).
Invocation: `driver.rs` is appended to `src/app/help.rs` of a container-local copy (`/tmp/w`, `/w` is never modified)
as `mod tc_bench`; it builds `OptBuilder`s and two `Help` writers (hide_pv false/true, color off, width 120) before timing
and calls `help.spec_vals(&opt)`. `check` hashes all returned strings with FNV-1a 64. Run with `cargo test --release`.
