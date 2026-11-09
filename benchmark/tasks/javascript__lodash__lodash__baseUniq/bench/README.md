`baseUniq` is internal; the driver calls the public `_.uniq(a)`, `_.uniqBy(a, iteratee)` and `_.uniqWith(a, comparator)` from `require('/w/lodash.js')`, which delegate straight to it.
Workload: arrays generated before timing from a seeded LCG over a key domain (few / many / mostly-distinct keys): integers with -0/+0 and NaN, strings, shared objects, mixed primitives with symbols, floats; iteratees are a floor key function or the `'id'` property shorthand, comparators `_.eq` or id-equality (comparator arrays are 40x shorter since that mode is pairwise).
Array length 500-1,000 / 5,000-10,000 / 50,000-100,000 (S/M/L), 40 cases each; S adds tiny/empty arrays.
The digest covers each result element (sign of zero, NaN, symbols, object ids, and whether objects are the original references).
