The target `stringify` is a private (non-exported) recursive helper of `lib/stringify.js`, so the driver calls
the narrowest public entry point, `require('/w/lib/index.js').stringify(obj, opts)`, whose cost is dominated by it.
Workload: tagged JSON cases `{obj, opts}` of nested objects/arrays with unicode/special-char keys and string, number,
boolean, null, undefined, Date, Buffer and Symbol leaves, combined with random option sets (all array formats, dots,
strict nulls, skipNulls, encodeValuesOnly, encode:false, RFC1738, iso-8859-1, sentinels, sort/filter/encoder/
serializeDate functions named in the JSON and built by the driver). S also holds the test-suite edge cases.
Sizing: 80 random cases per size with ~8 / ~100 / ~1100 leaf values per case (S/M/L); nesting depth grows with size.
The private helper is reached through the public `qs.stringify`, whose cost it dominates (it does all per-value work).
