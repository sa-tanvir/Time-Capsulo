You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** go
- **File:** `version.go`

## Imports / includes available in this file

```
import "bytes"
import "encoding/json"
import "errors"
import "fmt"
import "regexp"
import "strconv"
import "strings"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(r rune)bool
(v Version)IncMajor
(v Version)IncMinor
(v Version)IncPatch
(v Version)Major
(v Version)MarshalJSON
(v Version)Metadata
(v Version)Minor
(v Version)Patch
(v Version)Prerelease
(v Version)SetMetadata metadata string
(v Version)SetPrerelease prerelease string
(v Version)String
(v Version)originalVPrefix
(v*Version)Compare o * Version
(v*Version)Equal o * Version
(v*Version)GreaterThan o * Version
(v*Version)LessThan o * Version
(v*Version)Original
(v*Version)UnmarshalJSON b [ ] byte
MustParse v string
NewVersion v string
StrictNewVersion v string
comparePrePart s , o string
compareSegment v , o uint64
init
validateMetadata m string
validatePrerelease p string
```

## Package-level types, constants and variables (`version.go`, you may use them)

```go
// Version represents a single semantic version.
type Version struct {
	major, minor, patch uint64
	pre                 string
	metadata            string
	original            string
}

var (
	// ErrInvalidSemVer is returned a version is found to be invalid when
	// being parsed.
	ErrInvalidSemVer = errors.New("Invalid Semantic Version")

	// ErrEmptyString is returned when an empty string is passed in for parsing.
	ErrEmptyString = errors.New("Version string empty")

	// ErrInvalidCharacters is returned when invalid characters are found as
	// part of a version
	ErrInvalidCharacters = errors.New("Invalid characters in version")

	// ErrSegmentStartsZero is returned when a version segment starts with 0.
	// This is invalid in SemVer.
	ErrSegmentStartsZero = errors.New("Version segment starts with 0")

	// ErrInvalidMetadata is returned when the metadata is an invalid format
	ErrInvalidMetadata = errors.New("Invalid Metadata string")

	// ErrInvalidPrerelease is returned when the pre-release is an invalid format
	ErrInvalidPrerelease = errors.New("Invalid Prerelease string")
)

const num string = "0123456789"
const allowed string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-" + num
```

## Instance state of `Version`

| field | type | meaning |
|---|---|---|
| `major`, `minor`, `patch` | `uint64` | the three numeric components |
| `pre` | `string` | pre-release identifiers joined by `.`, without the leading `-` (`""` = no pre-release) |
| `metadata` | `string` | build metadata joined by `.`, without the leading `+` (`""` = no metadata) |
| `original` | `string` | the exact text the version was parsed from (may start with `v`) |

The accessors `Major()`, `Minor()`, `Patch()`, `Prerelease()`, `Metadata()` and
`Original()` return these fields unchanged.

## Helper functions in this file (contracts)

```go
// Like strings.ContainsAny but does an only instead of any: true when every
// rune of s occurs in comp (true for an empty s).
func containsOnly(s string, comp string) bool

// Splits p on every '.' and checks the identifiers in order, returning the
// first error found, else nil. An identifier made only of ASCII digits
// (this includes the empty identifier) is rejected with ErrSegmentStartsZero
// when it is longer than one character and starts with '0'. Any other
// identifier containing a rune outside [0-9A-Za-z-] is rejected with
// ErrInvalidPrerelease. Empty identifiers are accepted
// (validatePrerelease("a..b") == nil, validatePrerelease("") == nil).
func validatePrerelease(p string) error

// Splits m on every '.'; returns ErrInvalidMetadata if any identifier
// contains a rune outside [0-9A-Za-z-], else nil. Empty identifiers and
// leading zeros are accepted (validateMetadata("01..x") == nil).
func validateMetadata(m string) error

// -1, 0 or 1 for v < o, v == o, v > o.
func compareSegment(v, o uint64) int


// Orders two single pre-release identifiers s and o; returns -1, 0 or 1:
//   - s == o (same string)                    -> 0
//   - else s == ""                            -> -1;  else o == "" -> 1
//   - "numeric" means strconv.ParseUint(x, 10, 64) succeeds
//   - neither numeric                         -> 1 if s > o (byte-wise), else -1
//   - only s numeric                          -> -1;  only o numeric -> 1
//   - both numeric                            -> 1 if value(s) > value(o), else -1
//     (so equal values with different text, e.g. "01" vs "1", give -1)
func comparePrePart(s, o string) int
```

=== STUB ===
```go
func comparePrerelease(v, o string) int {
    // TODO: implement according to the specification
}
```
