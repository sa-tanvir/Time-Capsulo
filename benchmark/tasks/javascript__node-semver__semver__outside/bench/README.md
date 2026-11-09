Calls `semver.outside(version, rangeString, hilo, options)` once per case with raw strings (so range parsing is part of the measured work, as in the function).
Random ranges (carets, tildes, x-ranges, hyphen ranges, operators, prereleases) with up to 2x3 / 6x8 / 30x20 sets x comparators (S/M/L); hilo `<` or `>`; options undefined/loose/includePrerelease.
S adds the gtr/ltr test-suite cases in both directions and an invalid hilo. Digest: boolean or error per case.
