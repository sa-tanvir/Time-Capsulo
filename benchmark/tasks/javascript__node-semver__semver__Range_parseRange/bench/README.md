Calls `recv.parseRange(part)` where `recv = new Range('*', options)` is built outside the timed region.
Parts are random `||`-free comparator sets with 1-4 / 20-40 / 200-400 tokens (S/M/L) of operators (with/without spaces), carets, tildes, x-ranges, stars, partial versions and hyphen ranges, sometimes padded; options undefined/loose/includePrerelease.
S adds every `||` part of a fixed list of test-suite ranges in three option modes. Digest: comparator values/operators/options, or the error.
