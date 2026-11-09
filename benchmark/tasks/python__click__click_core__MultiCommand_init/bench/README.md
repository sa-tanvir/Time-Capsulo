Workload: 16 seeded parameter lists per size with ~10 (S), 100 (M), 1000 (L) parameters (60% options, the rest
required positional arguments; every 4th list contains one optional argument — `required=False` or `nargs=-1`),
and 1000 constructor calls mixing chain on/off, explicit/derived `no_args_is_help` and `subcommand_metavar`,
result callbacks, help text and `hidden`. The driver calls `click.MultiCommand(name, params=..., **kw)` and hashes the
resulting attributes, or the `RuntimeError` message.
