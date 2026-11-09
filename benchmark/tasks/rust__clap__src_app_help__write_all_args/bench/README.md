Workload: one App per line: UnifiedHelpMessage on/off, help width, numbers of flags/options/positionals/subcommands,
percentage hidden and an optional `help` subcommand; the driver expands each line from its seed (xorshift) into named
args with help texts, display orders, value names, possible values, defaults, NextLineHelp. S covers every section
combination (empty, single section, all hidden, unified); M/L hold apps with 10-80 and 100-800 elements per kind.
Invocation: `driver.rs` is appended to `src/app/help.rs` of a container-local copy (`/tmp/w`, `/w` never modified) as
`mod tc_bench`; apps are built before timing; one `Help` writer (colour off) over an in-memory sink is reused and
`help.write_all_args(&app.p)` is called. `check` hashes all written bytes per app (FNV-1a 64).
