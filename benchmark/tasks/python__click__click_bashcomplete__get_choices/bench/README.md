Workload: 200 seeded completion queries `(tree, args, incomplete)` per size over six command trees defined in
`bench/clis.py` (option choices, `=`-joined options, multiple/nargs=2 options, chained groups, deep
groups with `autocompletion` callbacks, hidden options/commands, variadic arguments); 75% of the queries repeat option/subcommand/value units ~K times, K = 5 (S), 50 (M), 500 (L).
The driver calls `get_choices(cli, "prog", args_copy, incomplete)` for each query (fresh copies of
`args` are prepared before timing) and hashes the `repr` of each returned list.
