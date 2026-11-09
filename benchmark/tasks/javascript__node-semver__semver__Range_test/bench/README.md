Calls `range.test(version)` with the Range built outside the timed region; versions are strings (parsed by the method), pre-built SemVer objects, or falsy/invalid values.
Ranges are `||` lists of 1-4 / 30-60 / 300-600 small sets (carets, tildes, bounded pairs, x-ranges) for S/M/L, 8 versions each; S uses the shared fixed range list with 19 versions each.
Digest: booleans.
