Workload: 24 seeded parameters per size (value options with nargs 1-3, flags, `--x/--no-x` switches,
counting options, arguments) and random typed-word lists drawn from their spellings plus `=`, values
and unknown options (often ending near a spelling of the queried parameter); 300 queries per size with argument lists of up to 10 (S), 100 (M), 1000 (L) words.
The driver calls `is_incomplete_option(args, param)` for every query, `passes` times, and hashes the
sequence of boolean results.
