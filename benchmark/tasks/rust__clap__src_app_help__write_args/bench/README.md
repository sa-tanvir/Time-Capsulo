Workload: one argument list per line: flags+options chained (unified style), flags only, options only, or positionals,
with help width and hidden percentage; the driver expands each line from its seed (xorshift) into uniquely named args
with help texts, display orders (0-4 or default), value names, possible values, defaults, NextLineHelp (hidden +
NextLineHelp stays visible). S covers empty/single/hidden/ordered lists; M/L hold 30-300 and 300-3000 args per kind.
Invocation: `driver.rs` is appended to `src/app/help.rs` of a container-local copy (`/tmp/w`, `/w` never modified) as
`mod tc_bench`; apps are built before timing; one `Help` writer (colour off) over an in-memory sink is reused and
`help.write_args(iter)` is called. `check` hashes the written bytes plus the resulting `longest` per case (FNV-1a 64).
