Workload: seeded random command trees (names with occasional `:`), with hidden/deprecated/non-runnable
commands, aliases, ValidArgs, ArgAliases and string/bool/int/slice flags (local and persistent, some hidden
or deprecated, at most one bash-completion annotation each so output is deterministic). S = 300 trees of
depth 1; M = 40 trees of depth 2 (<= 5 children); L = 6 trees of depth 3 (<= 7 children, <= 10 flags/node).
The driver (Go test in package `cobra`) builds the trees and installs the help command/flag before timing,
then calls `gen(buf, cmd)` on the root (sometimes a sub-command) into a reset buffer; check hashes the text.
