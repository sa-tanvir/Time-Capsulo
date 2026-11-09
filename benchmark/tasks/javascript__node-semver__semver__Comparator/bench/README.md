Calls `new Comparator(input, options)` once per case. Comparator strings are an operator, optional space and a version whose length grows with the size (~12 / ~70 / ~230 chars: long prerelease and build parts; versions are limited to 256 chars), strict or loose (with v/= prefixes).
S adds fixed valid/invalid comparators in three option modes and existing-Comparator inputs (built outside the timed region).
Digest: identity flag, value, operator, loose, options, semver version/raw, or the error.
