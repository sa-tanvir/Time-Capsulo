You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func StrictNewVersion(v string) (*Version, error)`

## 1. Component overview

`StrictNewVersion` belongs to the `semver` package
(`github.com/Masterminds/semver/v3`). It parses a string that must be a
complete Semantic Version 2.0.0 — `MAJOR.MINOR.PATCH`, optionally followed by
`-PRERELEASE` and/or `+METADATA` — into a `*Version` (fields described under
"Instance state of `Version`" in the context). Unlike the lenient `NewVersion`
it does not coerce: no leading `v`, no missing components. It is meant to be
fast (callers use it on hot paths), so avoid needless work and allocations.

## 2. Functional requirements

**Splitting.** Conceptually the input is cut at its first two `.` characters
into three pieces: major, minor, and a *tail* (everything after the second
dot). Only the tail may carry a pre-release or metadata:

1. If the tail contains a `+`, everything after the **first** `+` is the
   metadata and is removed from the tail.
2. Then, if the remaining tail contains a `-`, everything after the **first**
   `-` is the pre-release and is removed from the tail. (So a `-` inside the
   metadata is never mistaken for a pre-release: `1.2.3+b-c` has metadata
   `b-c` and no pre-release; `1.2.3-a-b+c-d` has pre-release `a-b` and
   metadata `c-d`.)
3. What remains of the tail is the patch piece.

**Checks, in this order; the first failure is returned with a `nil` version:**

1. Empty input -> `ErrEmptyString`.
2. Fewer than two `.` characters (fewer than three pieces) -> `ErrInvalidSemVer`.
   Extra dots after the second one end up in the tail (`1.2.3.4` has the
   patch piece `3.4`).
3. For the major, then the minor, then the patch piece (finish all checks on
   one piece before the next): if it contains any character other than ASCII
   `0`-`9` -> `ErrInvalidCharacters`; else if it is longer than one character
   and starts with `0` -> `ErrSegmentStartsZero`.
4. Convert major, minor, patch to `uint64` with `strconv.ParseUint(piece, 10, 64)`;
   if that fails (empty piece such as in `1..3`, or a value above
   18446744073709551615), return the error from `strconv` unchanged.
5. If the pre-release is non-empty, check its `.`-separated identifiers in
   order: an identifier made only of digits that is longer than one character
   and starts with `0` -> `ErrSegmentStartsZero`; otherwise an identifier
   containing a character outside `[0-9A-Za-z-]` -> `ErrInvalidPrerelease`.
6. If the metadata is non-empty, any of its `.`-separated identifiers
   containing a character outside `[0-9A-Za-z-]` -> `ErrInvalidMetadata`
   (leading zeros are allowed in metadata).

Empty identifiers (e.g. `1.2.3-a..b`) are **not** rejected, and a bare
trailing `-` or `+` simply yields an empty pre-release / metadata
(`1.2.3-`, `1.2.3+` and `1.2.3-+` all parse as 1.2.3).

**Success.** Return a new `*Version` with `major`, `minor`, `patch` set to the
parsed numbers, `pre` and `metadata` set to the extracted strings (without
the `-` / `+`; `""` when absent), `original` set to the input string exactly,
and a `nil` error.

## 3. Input specification

- `v`: any string, possibly empty, possibly containing non-ASCII characters,
  whitespace or newlines. Valid inputs may have long pre-release / metadata
  parts (dozens of identifiers).

## 4. Output specification

- On success: non-nil `*Version`, `nil` error.
- On failure: `nil` version and a non-nil error; one of the package error
  variables listed in the context, or the `strconv` error from step 4.

## 5. Edge cases and constraints

| input | result |
|---|---|
| `"1.2.3"` | 1.2.3 |
| `"1.2.3+test.01"` | 1.2.3, metadata `test.01` |
| `"1.2.3-alpha.-1"` | 1.2.3, pre `alpha.-1` |
| `"1.2.0-x.Y.0+metadata-width-hypen"` | 1.2.0, pre `x.Y.0`, metadata `metadata-width-hypen` |
| `"1.2.3-rc1-with-hypen"` | 1.2.3, pre `rc1-with-hypen` |
| `"1.2.2147483648"`, `"2147483648.3.0"` | parse fine (64-bit components) |
| `""` | `ErrEmptyString` |
| `"1"`, `"foo"`, `"1.0"`, `"v1.0"`, `"1.2-5"`, `"\n1.2"` | `ErrInvalidSemVer` |
| `"v1.2.3"`, `"1.2.beta"`, `"1.2-beta.5"`, `"1.2.3.4"`, `"1.2.3 "` | `ErrInvalidCharacters` |
| `"01.2.3"`, `"01.a.3"` | `ErrSegmentStartsZero` (major checked fully first) |
| `"a.01.3"` | `ErrInvalidCharacters` |
| `"1.2.3-alpha.01"`, `"1.2.3-00"` | `ErrSegmentStartsZero` (`1.2.3-0a` is valid) |
| `"1.2.3-é"`, `"1.2.3-a_b+c_d"` | `ErrInvalidPrerelease` (pre-release checked before metadata) |
| `"1.2.3+meta+more"` | `ErrInvalidMetadata` (second `+` belongs to the metadata) |
| `"18446744073709551616.0.0"` | the `strconv.ParseUint` range error |

- No input may cause a panic. The function has no side effects and is safe
  for concurrent use.

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

=== STUB ===
```go
func StrictNewVersion(v string) (*Version, error) {
    // TODO: implement according to the specification
}
```
