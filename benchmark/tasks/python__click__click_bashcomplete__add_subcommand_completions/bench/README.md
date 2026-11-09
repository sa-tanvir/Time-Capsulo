Workload: 300 seeded `(tree, args, incomplete)` queries per size over the command trees in `bench/clis.py`, mostly
on a large tree (root, a chained group and a nested chained group of ~10 (S), 100 (M), 1000 (L) commands each, with
hidden commands, short/long help) plus the test-suite style trees. Contexts are resolved with
`resolve_ctx` before timing; the driver calls `add_subcommand_completions(ctx, incomplete, out)` per
query (`passes` times) and hashes the return value and the resulting `out` list (in order).
