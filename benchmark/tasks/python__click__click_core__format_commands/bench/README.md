Workload: seeded multi commands whose `list_commands` returns up to K names (K = 8 S, 80 M, 800 L): mostly visible
commands with assorted help/short_help (some registered under a name different from `cmd.name`), plus hidden
commands, hidden subgroups, unknown (ghost) names and duplicates; formatter widths 20-120. S starts with edge cases
(empty, all hidden, hidden group, ghost only, the click test docstrings). Commands, contexts and fresh
`HelpFormatter`s are built outside the timed region; the driver calls `mc.format_commands(ctx, formatter)` and
hashes the formatter text.
