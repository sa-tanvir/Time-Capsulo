Calls `isEmail(str[, options])` directly; the driver transpiles `/w/src/lib/isEmail.js` with the repo's Babel config and calls the default export once per case.
Workload: random local parts (atext, UTF-8, quoted, double dots) at assorted domains (Gmail, IDN, IP literals, bad hosts), display-name forms (quoted/unquoted, illegal characters, padded names) and over-long addresses, under 11 option combinations.
S additionally holds every test-suite address under every option combination, quoted/`@`-in-local-part corner cases and non-string inputs (TypeError).
Sizing: display-name padding and long-local-part runs scale 1x / 10x / 100x (mean input length ~35 / ~160 / ~1150 characters); 400 random cases per size. Addresses themselves are capped at 254 characters by the function's own rules, so per-call cost grows only mildly.
Option objects are rebuilt outside the timed region on every pass.
