Calls `semverObj.inc(release, identifier)` on a fresh `new SemVer(v)` per case and per repeat (rebuilt outside the timed region, since inc mutates).
For M/L the receiver's `prerelease` array is replaced by a long list (~15-45 / ~150-450 identifiers, mostly non-numeric, often with the only number at the front) so that the `pre`/`prerelease` bumps scan far.
Releases are weighted toward `prerelease`/`pre`; identifiers are random tags or the existing first tag. S holds the test-suite cases (including invalid release types).
Digest: resulting version, raw, major/minor/patch, prerelease and build arrays, or the error.
