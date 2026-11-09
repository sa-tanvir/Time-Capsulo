Calls `semver.coerce(input, options)` once per case, options `undefined` / `{rtl:false}` / `{rtl:true}`.
Inputs are random texts (~40 / ~400 / ~4000 chars for S/M/L) mixing words, dotted digit groups, embedded versions and 15-20 digit runs; in 30% of them the digits appear only at the end.
S adds the test-suite inputs (overlong components, rtl examples, numbers, null, objects, an existing SemVer) in both modes.
Digest: null, or identity flag + version + raw + prerelease of the result.
