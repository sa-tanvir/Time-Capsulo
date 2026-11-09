The target is `module.exports` of `lib/stringify.js` (= `qs.stringify`); the driver calls
`require('/w/lib/index.js').stringify(obj, opts)` once per case. Thrown errors are hashed as `ERR:<name>:<message>`.
Workload: tagged JSON cases `{obj, opts}` of nested objects/arrays with unicode/special-char keys and string, number,
boolean, null, undefined, Date, Buffer and Symbol leaves, combined with random option sets (all array formats, dots,
strict nulls, skipNulls, encodeValuesOnly, encode:false, RFC1738, iso-8859-1, sentinels, sort/filter/encoder/
serializeDate functions named in the JSON and built by the driver). S also holds test-suite edge cases and invalid options.
Sizing: 80 random cases per size with ~8 / ~100 / ~1100 leaf values per case (S/M/L); nesting depth grows with size.
