Workload: seeded flags `[NoOptDefVal, Annotations]`: 15% value-less flags, 60% with a filename-extension
annotation, 25% with a directory annotation, plus unrelated annotation keys (never both relevant keys at once,
so the result is deterministic). S = 5000 flags (<= 3 patterns, fixed edge cases); M = 2000 flags (15-30
patterns); L = 200 flags (150-300 patterns, up to 40 extra keys). The driver (Go test in package `cobra`)
builds `*pflag.Flag` values before timing and calls `zshCompGenFlagEntryExtras(f)` directly.
