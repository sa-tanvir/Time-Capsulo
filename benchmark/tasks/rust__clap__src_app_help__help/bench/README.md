Workload: one argument per line (option `--opt`, flag `-f` or positional; optional NextLineHelp) with short/long help
texts (literal or generated word streams with `{n}` markers or real newlines), the special-values suffix, and the writer
state (next_line_help, use_long, force_next_line, term width incl. unlimited, longest). S holds help-test shapes and edge
cases (no help, `{n}`, forced next line, tiny widths); M/L hold 50-500 and 1000-10000-word help texts that need wrapping.
Invocation: `driver.rs` is appended to `src/app/help.rs` of a container-local copy (`/tmp/w`, `/w` never modified) as
`mod tc_bench`; one `Help` writer (colour off) over an in-memory sink is reused, its fields set per case, then
`help.help(&arg, spec)` is called. `check` hashes all written bytes per case (FNV-1a 64).
