The driver bundles `/w/src/moment.js` plus `src/lib/duration/valid.js` with the repo's rollup and calls `isDurationValid(m)` directly.
Workload: normalized duration input objects (canonical unit keys in random order, occasionally non-canonical keys) with integer, decimal, numeric-string, null/undefined, NaN, +-Infinity, boolean and junk values; S also has the duration-validity test cases.
The object size is bounded by the 9 units, so S/M/L scale the number of calls: ~2,000 / 20,000 / 200,000 (L = 20,000 distinct objects used 10 times).
