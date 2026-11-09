Workload: seeded commands, each `[annotation JSON or null, ValidArgs]`: random file/word hints at random
positions (including positions >= 10 to exercise string ordering), optional ValidArgs, ~2% unknown hint
types and an invalid-JSON case (error paths). S = 2000 commands with <= 3 hints; M = 300 with <= 30;
L = 30 with <= 300 hints of <= 30 options. The driver (Go test in package `cobra`) builds the
`*Command` values before timing and calls the function directly; check mode also hashes the command state.
