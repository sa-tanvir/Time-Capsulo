Calls `isIn(str, options)` directly; the driver transpiles `/w/src/lib/isIn.js` with the repo's Babel config and calls the default export once per case.
Workload: arrays of mixed values (strings, numbers, booleans, null, objects with/without toString), plain objects keyed by random words, long haystack strings, and non-collection options (undefined, numbers, booleans, null -> TypeError); about half the probes are taken from the collection.
S additionally holds the test-suite collections and probes.
Sizing: collections of ~10 / ~100 / ~1000 entries (strings ~10x that many characters), 300 random cases per size.
