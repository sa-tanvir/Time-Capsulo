Calls `isFQDN(str[, options])` directly; the driver transpiles `/w/src/lib/isFQDN.js` with the repo's Babel config and calls the default export once per case.
Workload: dotted names built from LDH, Unicode and underscore labels with valid and invalid TLDs (IDN `xn--`, Cyrillic, CJK, spaces, U+3000, U+FEFF, tag space), optional trailing dot and injected bad characters, under all option combinations.
S additionally holds the test-suite names, label-length boundaries (63/64), empty labels and non-string inputs (TypeError).
Sizing: mean name length ~25 / ~250 / ~2500 characters (S/M/L), 300 random cases each; long names repeat a 20-label block.
Option objects are rebuilt outside the timed region on every pass.
