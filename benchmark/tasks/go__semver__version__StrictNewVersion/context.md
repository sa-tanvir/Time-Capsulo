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
comparePrePart s , o string
comparePrerelease v , o string
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

// Orders two pre-release strings (without the leading '-') by SemVer
// precedence; returns -1, 0 or 1.
func comparePrerelease(v, o string) int

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
