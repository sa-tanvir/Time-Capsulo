Workload: seeded (toCheck, toMatch, canonicalKey) triples shaped like header matchers: lower/upper-case
keys, empty required values (presence only), missing keys/values, empty value lists, unrelated extra keys.
Entries per toCheck: 3 (S), 30 (M), 300 (L). S starts with the test-suite cases.
Driver: Go test copied into package `mux`; maps are built before timing, then `matchMapWithString` is called.
