`arrayLikeKeys` is internal to lodash.js; the driver calls the public `_.keys(v)` / `_.keysIn(v)` from `require('/w/lodash.js')`, which for array-like values only delegate to `arrayLikeKeys(v)` / `arrayLikeKeys(v, true)`.
Workload: arrays (dense or with periodic holes), `arguments` objects, typed arrays, Buffers, string primitives and `String` objects, and plain `{length: n, 0..n-1}` objects, built before timing, with extra own enumerable keys (index-like, out-of-range, `length`/`offset`/`buffer`-style names) and optional custom prototypes with enumerable keys; half the cases use `keysIn`.
S also holds the test-suite style edge cases. Length per case: ~50-100 / 500-1,000 / 5,000-10,000 (S/M/L), 120 random cases each.
The digest covers each returned key array (order included).
