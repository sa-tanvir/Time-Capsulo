Workload: 1000 seeded random `click.Option` declarations per size (value options with assorted types/metavars/nargs,
flags, `--x/--no-x` and `/x;/no-x` pairs, counting options), with random help text, hidden/required,
`show_default` (bool or string), `show_envvar`, explicit/list/automatic env vars and contexts with
`auto_envvar_prefix` None/APP/TEST. Per-case scale: up to K extra aliases, env-var lists / list defaults of up to K
entries and ~K extra help words, K = 2 (S), 20 (M), 200 (L). Options and contexts are built before timing; the driver
calls `opt.get_help_record(ctx)` for every option and hashes the `repr` of each record.
