Calls `isIP(str[, version])` directly; the driver transpiles `/w/src/lib/isIP.js` with the repo's Babel config and calls the default export once per case.
Workload: random IPv4 (incl. out-of-range groups), IPv6 with/without `::`, IPv4 tails and `%zone` suffixes, long colon-separated field runs and repeated junk, with version omitted, 4, 6, '4', '6', '' or 10.
S additionally holds the test-suite addresses and boundary cases (field counts, misplaced `::`, zones) under every version, plus version 0/null and non-string input (TypeError).
Sizing: zone ids / junk runs scale ~1x / 10x / 100x (mean input length ~20 / ~200 / ~2000 characters), 400 random cases per size.
