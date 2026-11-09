Workload: seeded constraint strings. S starts with every constraint string from the package tests
plus edge cases (empty / blank segments, parser errors, hyphen ranges, wildcards), then random
strings of 1-3 constraints; M has 5-15 and L 40-90 constraints per string, split into OR groups
of up to 6, mixing all operators and aliases, spacing/comma separators, hyphen ranges, wildcards,
`v` prefixes, pre-releases and metadata; about 4% contain an invalid segment. The driver (a Go
test copied into the `semver` package) calls `NewConstraint(s)` and hashes the full parsed
structure (every constraint's operator, text, version fields and flags) or the error message.
