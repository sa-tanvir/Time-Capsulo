Workload: 60 seeded cases per size; each case is an `OptionParser` (with or without a `Context`) holding
~10 (S), 100 (M), 1000 (L) registered long options (prefixes `--`, `-`, `+`, `/`, `++`; all five actions; nargs 1-3),
a remaining-args list of 2.4x that length and 0.8x that many `(opt, explicit_value)` calls, incl. unknown/prefix
names, `=value` on flags and running out of args. The driver calls `parser._match_long_opt(opt, ev, state)` on a fresh
`ParsingState` per case and hashes rargs after each call, the error type/message/option/possibilities, and final opts/order.
