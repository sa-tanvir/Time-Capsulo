Calls the exported `require('/w/lib/utils.js').arrayToObject(array, options)` directly, once per case.
Workload: arrays of up to 60k elements built by the driver (before timing) by cycling a small JSON base list of
strings, numbers, null, booleans, small objects/arrays and undefined, with periodic explicit undefineds and holes;
options are absent, `{}`, or `plainObjects` true/false/1. S also holds tiny edge cases (empty, all-undefined, sparse).
The digest covers each result's prototype (null or not), key list and values.
Sizing: mean array length ~100 / ~1000 / ~10000 (S/M/L), 300 random cases each.
