Workload: seeded `[i, Tipe, Options]` triples: ~45% file-glob hints, ~52% word hints, ~3% unknown types
(error path), options containing spaces, quotes, backslashes and non-ASCII. S = 4000 cases with up to
4 options plus fixed edge cases (empty/nil options, unknown types); M = 1000 cases with 20-40 options;
L = 100 cases with 200-400 options. The driver is a Go test copied into package `cobra`; it calls
`zshCompRenderZshCompArgHint(i, z)` directly and hashes results ("ERR" for errors) or times the calls.
