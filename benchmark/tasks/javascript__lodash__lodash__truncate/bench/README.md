Calls the public `_.truncate(string, options)` from `require('/w/lodash.js')` once per case.
Workload: texts built (before timing) from a seeded LCG over a word list, ~35% of them containing astral emoji, ZWJ sequences, flags or combining marks; `length` from 1/4 of the text up to the full text (plus tiny, negative and over-long lengths), omissions ('...', '', ' [...]', null/undefined, astral), separators none / string / regex (global and non-global).
S also holds the test-suite cases. Words per text: 15-30 / 150-300 / 1,500-3,000 (S/M/L), 300 random cases each.
The digest covers every returned string.
