testSet is module-private; it is reached through `range.test(semverObj)` (Range.prototype.test only loops over the sets calling testSet), with Range and SemVer objects pre-built outside the timed region.
Ranges have 1-2 sets of 1-6 / 30-60 / 300-600 comparators (S/M/L), mostly wide bounds that the generated versions satisfy, some rejecting comparators and prerelease comparators, so the prerelease rule scans the whole set.
6 versions per range (60% prereleases); options undefined or includePrerelease. S adds test-suite ranges. Digest: booleans.
