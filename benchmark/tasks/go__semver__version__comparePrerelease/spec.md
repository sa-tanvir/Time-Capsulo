# Functional specification: `func comparePrerelease(v, o string) int`

## 1. Component overview

`comparePrerelease` belongs to the `semver` package
(`github.com/Masterminds/semver/v3`). It orders two pre-release strings by
Semantic Versioning precedence. A pre-release string is the part of a version
after the `-` and before any `+`, without the `-` itself, e.g. `"beta.2"` in
`"4.2.0-beta.2+build.7"`. It consists of identifiers separated by `.`.

`(*Version).Compare` calls it when two versions have equal major, minor and
patch and both have a non-empty pre-release; constraint checks also call it
(sometimes with an empty string on one or both sides). It therefore decides
results such as `4.2.0-alpha < 4.2.0-beta`, `3.2.0-beta.4 > 3.2.0-beta.2` and
`7.43.0-SNAPSHOT.99 < 7.43.0-SNAPSHOT.103`.

## 2. Functional requirements

Return `-1` if `v` has lower precedence than `o`, `1` if higher, `0` if equal.

1. **Identifiers.** Split each string on every `.` into a list of
   identifiers. Empty identifiers are kept (`""` is a list with one empty
   identifier; `"a."` is `["a", ""]`).
2. **Position by position.** Compare the identifiers at position 0, 1, 2, ...
   up to the length of the longer list. When one list is shorter, its missing
   positions count as the empty identifier `""`. The first position whose
   identifiers differ in precedence decides the result. If no position decides
   it, return `0`.
3. **Comparing two identifiers `a` (from `v`) and `b` (from `o`):**
   1. If `a` and `b` are the same string, they are equal (move on).
   2. Otherwise, an empty identifier is lower than a non-empty one.
   3. An identifier is *numeric* when it is a valid unsigned base-10
      integer that fits in a `uint64`: only ASCII digits, at least one digit,
      no sign, value at most 18446744073709551615. Anything else, including
      `"-2"`, `"beta2"` and digit strings that overflow `uint64`, is
      *alphanumeric*.
   4. A numeric identifier is lower than an alphanumeric one.
   5. Two alphanumeric identifiers are ordered by plain byte-wise string
      comparison (Go `<` on strings: `"-"` < digits < upper-case < lower-case).
   6. Two numeric identifiers are ordered by integer value. If the values
      are equal but the strings differ (leading zeros, e.g. `"01"` and `"1"`),
      the result is `-1` whichever side is which.

Examples:

| `v` | `o` | result |
|---|---|---|
| `"beta"` | `"beta"` | `0` |
| `"alpha"` | `"beta"` | `-1` |
| `"beta.2"` | `"beta.1"` | `1` |
| `"beta2"` | `"beta1"` | `1` (alphanumeric, compared as text) |
| `"beta"` | `"beta.2"` | `-1` (shorter list, missing identifier is lowest) |
| `"beta.foo"` | `"beta"` | `1` |
| `"beta.4"` | `"beta.-2"` | `-1` (`-2` is alphanumeric, numeric is lower) |
| `"beta.-2"` | `"beta.-3"` | `-1` |
| `"beta.-3"` | `"beta.5"` | `1` |
| `"SNAPSHOT.99"` | `"SNAPSHOT.103"` | `-1` (numeric values) |
| `"SNAPSHOT.FOO"` | `"SNAPSHOT.103"` | `1` |
| `"18446744073709551616"` | `"1"` | `1` (overflows, so alphanumeric) |
| `""` | `"alpha"` | `-1` |
| `""` | `""` | `0` |

## 3. Input specification

- `v`, `o`: arbitrary strings, usually dot-separated identifiers made of
  `[0-9A-Za-z-]`. Either may be empty. They may hold many identifiers
  (dozens) and long shared prefixes.

## 4. Output specification

- An `int` that is exactly `-1`, `0` or `1`.

## 5. Edge cases and constraints

- Build metadata is never part of the inputs; no `+` handling is needed.
- `comparePrerelease(a, b) == -comparePrerelease(b, a)` holds except for the
  leading-zero case of rule 3.6.
- Trailing empty identifiers do not change the result against a list that is
  shorter by them: `"a."` vs `"a"` gives `0`.
- Pure function: no side effects, does not panic for any input, safe for
  concurrent use.
