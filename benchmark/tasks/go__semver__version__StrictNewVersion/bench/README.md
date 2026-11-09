Workload: seeded version strings, about 75% valid strict SemVer (components up to max uint64,
60% with pre-release, 40% with metadata) and 25% corrupted (leading `v`, missing components,
leading zeros, bad characters in core / pre-release / metadata, numeric pre-release with a
leading zero, a fourth component). S starts with the test-suite strings and edge cases.
Identifiers per pre-release/metadata: 1-2 (S), 3-10 (M), 23-70 (L). The driver (a Go test copied
into the `semver` package) calls `StrictNewVersion(s)` and hashes the fields or the error kind.
