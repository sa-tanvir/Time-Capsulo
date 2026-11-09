Workload: one command tree per line (root name, initial parent path, option/flag counts, subcommand fan-out, depth);
the driver expands it from its seed (xorshift) into Apps whose options/flags have short and/or long switches, help
texts containing quotes, backslashes and Unicode, possible values, and subcommands with/without `about`. S holds small
trees (incl. empty parent path and no args); M/L hold trees of depth <= 2 / <= 3 with 10-40 / 150-600 args per command.
Invocation: `driver.rs` is appended to `src/completions/fish.rs` of a container-local copy (`/tmp/w`, `/w` never
modified) as `mod tc_bench`; trees are built before timing; `gen_fish_inner(root, &FishGen::new(&app.p), parent, &mut buf)`
is called with a cleared buffer. `check` hashes the generated script text per case (FNV-1a 64).
