You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func NewConstraint(c string) (*Constraints, error)`

## 1. Component overview

`NewConstraint` belongs to the `semver` package
(`github.com/Masterminds/semver/v3`). It parses a version-constraint
expression such as `">= 1.2.3, < 2.0 || ^3"` into a `*Constraints` value that
versions can then be checked against (`Check`, `Validate`) or printed
(`String`). The expression language:

- **OR groups** are separated by `||`.
- Inside a group, **AND-ed constraints** are separated by commas and/or
  whitespace (`">= 1.2.3, < 2.0"`, `">= 1.2.3 < 2.0"` and even `">1<2"` all
  give two constraints). A trailing comma is accepted; a leading one is not.
- Each constraint is an optional operator (`=`, `!=`, `>`, `<`, `>=`, `=>`,
  `<=`, `=<`, `~`, `~>`, `^`, or none) followed by a version that may be
  partial or contain wildcards (`1`, `1.2`, `1.x`, `1.2.*`, `*`), may start
  with `v`, and may carry a pre-release and metadata.
- **Hyphen ranges** `A - B` (whitespace on both sides of the `-`) mean
  `>= A, <= B`. A `-` without surrounding whitespace is a pre-release
  separator, so `"1.1-3"` is one constraint (version 1.1 with pre-release `3`).

The helpers and regular expressions listed in the context (`rewriteRange`,
`parseConstraint`, `validConstraintRegex`, `findConstraintRegex`) define the
exact grammar and are meant to be used.

## 2. Functional requirements

1. **Range rewrite.** First rewrite every hyphen range in the whole input
   exactly as `rewriteRange` does (e.g. `"3 - 4 || => 3.0, < 4"` becomes
   `">= 3, <= 4|| => 3.0, < 4"`).
2. **OR split.** Split the rewritten string on every occurrence of `"||"`.
   Each piece is an OR segment, kept verbatim (surrounding whitespace is not
   trimmed). Segments are processed in order, left to right.
3. **Segment validation.** A segment is valid when it matches
   `validConstraintRegex` in full. For the first invalid segment, return
   `nil` and an error whose message is `"improper constraint: "` followed by
   the segment verbatim (for example `">= 1.2 || foo"` fails with
   `"improper constraint:  foo"`, with two spaces).
4. **Constraint extraction.** In a valid segment, take every non-overlapping
   match of `findConstraintRegex`, left to right; each match is one AND-ed
   constraint, parsed with `parseConstraint`. If `parseConstraint` fails
   (e.g. `">=1.2.3-01"`, a numeric pre-release with a leading zero, or a
   component too large for `uint64`), return `nil` and that error unchanged
   (its message is `"constraint Parser Error"`). Earlier segments are fully
   processed before later ones are validated, so the first problem in
   left-to-right order is the one reported.
5. **Result.** On success return `&Constraints{...}` whose `constraints`
   field has one entry per OR segment, in order, each being the list of
   parsed `*constraint` values of that segment, in order, and a `nil` error.

## 3. Input specification

- `c`: any string. Real inputs range from a single constraint to long
  expressions with dozens of constraints and several OR groups, with varied
  spacing.

## 4. Output specification

- Success: non-nil `*Constraints`, `nil` error. Every inner list is non-empty
  and every `*constraint` is exactly what `parseConstraint` returns for the
  corresponding match (operator, original text, version, wildcard flags).
- Failure: `nil` and a non-nil `error` with one of the two messages above.

## 5. Edge cases and constraints

| input | result (groups x constraints, or error) |
|---|---|
| `">= 1.1"` | 1 group, 1 constraint |
| `">40.50.60, < 50.70"` | 1 group, 2 constraints |
| `"2.0"`, `"v2.3.5-20161202202307-sha.e8fc5e5"`, `"1.1-3"` | 1 group, 1 constraint |
| `">= 1.2.3 < 2.0"`, `">= 1.2.3, < 2.0"`, `">1<2"`, `">=1.2.3,"` | 1 group (2, 2, 2, 1 constraints) |
| `"1.2 - 3.4 , 5 - 6"` | 1 group: `>=1.2`, `<=3.4`, `>=5`, `<=6` |
| `">= bar"`, `"BAR >= 1.2.3"`, `"foo"`, `",>=1.2.3"` | error `improper constraint: <segment>` |
| `""` | error `"improper constraint: "` |
| `">=1.2.3-01"`, `"99999999999999999999.0.0"` | error `"constraint Parser Error"` |

Inputs containing `||`:

- `">= 1.2.3 < 2.0 || => 3.0 < 4"` -> 2 groups of 2 constraints.
- `"3 - 4 || => 3.0, < 4"` -> 2 groups of 2 (the range becomes `>= 3`, `<= 4`).
- `"||"` -> error `"improper constraint: "`; `">=1 || "` -> error
  `"improper constraint:  "` (empty / blank segment).

Printing the result with `String()` must give, e.g.:
`"*"` -> `"*"`, `">= 1.2.3"` -> `">=1.2.3"`, `"1.2"` -> `"1.2"`,
`"2.x,   >=1.2.3 || >4.5.6, < 5.7"` -> `"2.x >=1.2.3 || >4.5.6 <5.7"`,
and that output must itself parse again. Checking must work as the operators
define, e.g. `">=1.1, <2, !=1.2.3 || > 3"` accepts 4.1.2 and rejects 3.0.0 and
1.2.3; `"1.1 - 2"` accepts 1.1.1.

- No input may cause a panic. The function has no side effects beyond
  allocation and is safe for concurrent use.

=== CONTEXT ===
# Context for the function to implement

- **Language:** go
- **File:** `constraints.go`

## Imports / includes available in this file

```
import "bytes"
import "errors"
import "fmt"
import "regexp"
import "strings"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(c*constraint)check v * Version
(c*constraint)string
(cs Constraints)Check v * Version
(cs Constraints)String
(cs Constraints)Validate v * Version
constraintCaret v * Version , c * constraint
constraintGreaterThan v * Version , c * constraint
constraintGreaterThanEqual v * Version , c * constraint
constraintLessThan v * Version , c * constraint
constraintLessThanEqual v * Version , c * constraint
constraintNotEqual v * Version , c * constraint
constraintTilde v * Version , c * constraint
constraintTildeOrEqual v * Version , c * constraint
init
isX x string
rewriteRange i string
```

## Types in this file

```go
// Constraints is one or more constraint that a semantic version can be
// checked against.
type Constraints struct {
	constraints [][]*constraint
}
```

`constraints` holds the OR groups in the order written; each OR group is the
list of AND-ed `*constraint` values in the order written. `Check` returns true
when every constraint of at least one group is satisfied; `String` prints
groups joined by `" || "` and the constraints of a group joined by a space.

```go
// An individual constraint (one operator/version pair)
type constraint struct {
	con        *Version // the concrete version compared against
	orig       string   // the version text as written, e.g. "1.2.x"
	origfunc   string   // the operator as written, e.g. ">=" or ""
	minorDirty bool
	dirty      bool
	patchDirty bool
}
```

## Helper functions in this file (contracts)

```go
// parseConstraint parses ONE operator/version pair (surrounding whitespace
// allowed), e.g. ">= 1.2", "~1.x", "!=4.1-alpha". It returns
// fmt.Errorf("improper constraint: %s", c) when c does not match
// constraintRegex, errors.New("constraint Parser Error") when the version part
// cannot be turned into a Version, and for c == "" a constraint equivalent to
// "*" (any release version).
func parseConstraint(c string) (*constraint, error)

// rewriteRange rewrites every hyphen range "A - B" (whitespace required around
// the '-') into ">= A, <= B" and returns the resulting string; strings without
// a range are returned unchanged. Example: "2 - 3, 4.0.0 - 5.1" ->
// ">= 2, <= 3,>= 4.0.0, <= 5.1".
func rewriteRange(i string) string
```

## Package-level variables defined in this file (you may use them)

```go
var constraintOps map[string]cfunc
var constraintMsg map[string]string
var constraintRegex *regexp.Regexp
var constraintRangeRegex *regexp.Regexp

// Used to find individual constraints within a multi-constraint string
var findConstraintRegex *regexp.Regexp

// Used to validate an segment of ANDs is valid
var validConstraintRegex *regexp.Regexp

const cvRegex string = `v?([0-9|x|X|\*]+)(\.[0-9|x|X|\*]+)?(\.[0-9|x|X|\*]+)?` +
	`(-([0-9A-Za-z\-]+(\.[0-9A-Za-z\-]+)*))?` +
	`(\+([0-9A-Za-z\-]+(\.[0-9A-Za-z\-]+)*))?`

// set up in init(); ops is the list of regexp.QuoteMeta(k) for every key k of
// constraintOps ("", "=", "!=", ">", "<", ">=", "=>", "<=", "=<", "~", "~>", "^")
//
//	constraintRegex      = regexp.MustCompile(fmt.Sprintf(`^\s*(%s)\s*(%s)\s*$`, strings.Join(ops, "|"), cvRegex))
//	constraintRangeRegex = regexp.MustCompile(fmt.Sprintf(`\s*(%s)\s+-\s+(%s)\s*`, cvRegex, cvRegex))
//	findConstraintRegex  = regexp.MustCompile(fmt.Sprintf(`(%s)\s*(%s)`, strings.Join(ops, "|"), cvRegex))
//	validConstraintRegex = regexp.MustCompile(fmt.Sprintf(`^(\s*(%s)\s*(%s)\s*\,?)+$`, strings.Join(ops, "|"), cvRegex))
```

=== STUB ===
```go
func NewConstraint(c string) (*Constraints, error) {
    // TODO: implement according to the specification
}
```
