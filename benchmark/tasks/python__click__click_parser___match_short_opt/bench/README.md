Workload: 100 seeded cases per size; each case is an `OptionParser` with 30 registered short options sharing one prefix
(`-`, `+` or `/`; flag/count/const/store/append actions, nargs 1-2), optionally a Context with a lower-casing
`token_normalize_func` and/or `ignore_unknown_options`, a few remaining args, and 5 cluster tokens of up to ~8 (S),
80 (M), 800 (L) characters (flags, unknown letters, a trailing value option with attached value).
The driver calls `parser._match_short_opt(token, state)` and hashes rargs/largs after each call, errors, and final opts/order.
