Workload: seeded command trees. Each case is a root whose children are hidden, deprecated, help-topic,
or chains of non-runnable commands ending in a hidden/deprecated/runnable leaf (so availability is only
decided deep in the tree); some cases add the auto-generated help command or target a sub-command.
S = 3000 roots (<= 3 children, chain depth 1, plus fixed edge cases); M = 300 (<= 30, depth 4);
L = 30 (<= 300, depth 12). The driver (Go test in package `doc`) builds the trees before timing and
calls `hasSeeAlso(cmd)` directly.
