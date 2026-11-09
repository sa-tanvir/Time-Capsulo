You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func PluralWord(quantity int, singular, plural string) string`

## 1. Component overview

`PluralWord` is part of package `english` (`github.com/dustin/go-humanize/english`),
which builds user-friendly English text. It picks the singular or plural
form of a noun for a given quantity. When no explicit plural is supplied it
guesses the plural with a small set of regular English rules plus a few
technical special cases. `Plural(quantity, singular, plural)` in the same
file uses it to produce strings like `"42 objects"` and `"1,234,567 objects"`.
Keep the function simple: it only needs the regular rules and the listed
special cases, not a full English dictionary.

## 2. Functional requirements

Apply the following rules in this order; the first one that matches decides
the result.

1. **Quantity one.** If `quantity == 1`, return `singular` unchanged (even if
   `plural` is non-empty). Every other quantity, including `0` and negative
   values, needs the plural form.
2. **Explicit plural.** If `plural` is not the empty string, return `plural`
   unchanged.
3. **Special technical plurals.** If `singular` is exactly (case-sensitive)
   `"index"`, `"matrix"` or `"vertex"`, return `"indices"`, `"matrices"` or
   `"vertices"` respectively (the `specialPlurals` table in the context).
4. **Sibilant endings.** If `singular` ends with `"s"`, `"sh"`, `"tch"` or `"x"`
   (lower-case, case-sensitive), return `singular + "es"`. Note that a plain
   `"ch"` ending that is not `"tch"` does not match this rule
   (`"church"` gives `"churchs"`), and upper-case endings do not match
   (`"BOX"` gives `"BOXs"`).
5. **Consonant + o.** If `singular` has at least 2 bytes, its last byte is a
   lower-case `'o'`, and the byte before it is not a vowel, return
   `singular + "es"`. Vowels are exactly the ASCII letters `a e i o u` and
   `A E I O U` (`'y'` is not a vowel; any non-ASCII byte is not a vowel).
6. **Consonant + y.** If `singular` has at least 2 bytes, its last byte is a
   lower-case `'y'`, and the byte before it is not a vowel (same vowel set),
   return `singular` without its final `'y'` followed by `"ies"`.
7. **Default.** Otherwise return `singular + "s"`.

The function is pure and safe for concurrent use.

Examples (`plural` is `""` unless shown):

| quantity | singular | plural | result |
|---|---|---|---|
| 1 | `"object"` | | `"object"` |
| 0 | `"object"` | | `"objects"` |
| -1 | `"object"` | | `"objects"` |
| 42 | `"object"` | | `"objects"` |
| 2 | `"vax"` | `"vaxen"` | `"vaxen"` |
| 1 | `"vax"` | `"vaxen"` | `"vax"` |
| 2 | `"index"` | | `"indices"` |
| 2 | `"Index"` | | `"Indexes"` |
| 2 | `"bus"` | | `"buses"` |
| 2 | `"bush"` | | `"bushes"` |
| 2 | `"watch"` | | `"watches"` |
| 2 | `"box"` | | `"boxes"` |
| 2 | `"hero"` | | `"heroes"` |
| 2 | `"radio"` | | `"radios"` |
| 2 | `"zoo"` | | `"zoos"` |
| 2 | `"lady"` | | `"ladies"` |
| 2 | `"day"` | | `"days"` |
| 2 | `"toy"` | | `"toys"` |

## 3. Input specification

- `quantity`: any `int`.
- `singular`: any string (may be empty, may contain non-ASCII UTF-8). Rules
  5 and 6 look at raw bytes, not runes.
- `plural`: any string; the empty string means "not given, guess it".

## 4. Output specification

- Returns a `string`: either `singular`, `plural`, a special plural, or
  `singular` with a suffix (`"es"`, `"s"`) or with its last `'y'` replaced by
  `"ies"`, as described above. No other transformation is applied (no case
  changes, no trimming).

## 5. Edge cases and constraints

- Empty `singular` with no plural: `""` gives `"s"`.
- Single-character words are too short for rules 5 and 6: `"o"` gives
  `"os"`, `"y"` gives `"ys"`; but rule 4 still applies: `"s"` gives `"ses"`,
  `"x"` gives `"xes"`.
- Rule 3 is checked before rule 4: `"matrix"` gives `"matrices"`, not
  `"matrixes"`.
- Upper-case final `'O'` or `'Y'` does not trigger rules 5 or 6
  (`"HERO"` gives `"HEROs"`); upper-case vowels do count as vowels for the
  preceding byte (`"bAy"` gives `"bAys"`).
- A non-ASCII byte before a final `'o'` counts as a consonant:
  `"néo"` gives `"néoes"` (the byte before `'o'` is the last byte of the
  UTF-8 encoding of `é`).
- The function never panics.

=== CONTEXT ===
# Context for the function to implement

- **Language:** go
- **File:** `english/words.go`

## Imports / includes available in this file

```
import "fmt"
import "strings"
import humanize "github.com/dustin/go-humanize"
```

## Other functions defined in the same file (signatures only; you may call them)

```
OxfordWordSeries words [ ] string , conjunction string
Plural quantity int , singular , plural string
WordSeries words [ ] string , conjunction string
```

## Package-level variables defined in this file (you may use them)

```go
// These are included because they are common technical terms.
var specialPlurals = map[string]string{
	"index":  "indices",
	"matrix": "matrices",
	"vertex": "vertices",
}

var sibilantEndings = []string{"s", "sh", "tch", "x"}

var isVowel = map[byte]bool{
	'A': true, 'E': true, 'I': true, 'O': true, 'U': true,
	'a': true, 'e': true, 'i': true, 'o': true, 'u': true,
}
```

=== STUB ===
```go
func PluralWord(quantity int, singular, plural string) string {
    // TODO: implement according to the specification
}
```
