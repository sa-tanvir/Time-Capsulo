Workload: 40 seeded command lines per size for seven driver-defined groups (chain / normal mode, with or without
result callback, `invoke_without_command`, a group with a required argument). Chained lines hold ~10 (S), 100 (M),
1000 (L) subcommand invocations (`a`, `b --format X`, `c VALUE`); normal-mode lines pass that many values to `collect`;
some lines have no, an unknown or a missing subcommand. The group context is built untimed with `make_context`, then
the driver calls `group.invoke(ctx)` and hashes the return value or UsageError message, the context fields and a call log.
