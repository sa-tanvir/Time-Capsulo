Workload: one argument per line (option / flag / positional with long, short, Multiple/RequireDelimiter/RequireEquals/
NextLineHelp, delimiter, num_vals or value names, generated help text, possible values) plus the writer state used for
it (next_line_help, term width incl. "unlimited", `longest` = signature width + extra). S holds help-test shapes and
edge cases; M/L hold arguments with 30-300 and 600-6000 value slots and proportionally longer help texts.
Invocation: `driver.rs` is appended to `src/app/help.rs` of a container-local copy (`/tmp/w`, `/w` is never modified) as
`mod tc_bench`; one `Help` writer (colour off) over an in-memory sink is reused, its fields are set per case, then
`help.val(&arg)` is called. `check` hashes written bytes + returned spec string + `force_next_line` (FNV-1a 64).
