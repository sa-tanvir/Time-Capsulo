The driver bundles `/w/src/moment.js` plus the target from `src/lib/utils/compare-arrays.js` with the repo's rollup and calls `compareArrays(array1, array2, dontConvert)` directly.
Workload: pairs of arrays of date-part numbers, numeric strings, locale-name parts and some non-numeric/fractional/null values, derived from each other by random edits, truncation or extension; `dontConvert` is true, false or absent.
S also holds hand-written edge cases (empty arrays, different lengths, strings vs numbers, `-0`, `Infinity`).
Array length grows ~10 / ~100 / ~1000 elements per case for S / M / L (600 / 500 / 400 cases).
