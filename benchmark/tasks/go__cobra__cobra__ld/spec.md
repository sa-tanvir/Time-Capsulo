# Functional specification: `func ld(s, t string, ignoreCase bool) int`

## 1. Component overview

`ld` belongs to package `cobra` (`github.com/spf13/cobra`), a library for
building command-line applications. When a user types an unknown sub-command,
cobra suggests similarly named commands ("Did you mean this?"). `ld` provides
the similarity measure: it returns the **Levenshtein edit distance** between
two strings, i.e. the minimum number of single-element insertions, deletions
and substitutions needed to turn `s` into `t`. `Command.SuggestionsFor` calls
it as `ld(typedName, cmd.Name(), true)` and suggests a command when the
result is `<= SuggestionsMinimumDistance` (default 2).

## 2. Functional requirements

1. Return the edit distance between `s` and `t`, where every insertion,
   deletion and substitution costs 1 (transpositions are **not** a single
   operation; swapping two adjacent different characters costs 2).
2. The strings are compared **byte by byte** (Go string indexing), not rune
   by rune. A multi-byte UTF-8 character therefore counts as several
   elements: `ld("é", "e", false) == 2` (`"é"` is 2 bytes, neither equal
   to `'e'`), and `ld("", "é", false) == 2`.
3. If `ignoreCase` is true, both strings are first converted with
   `strings.ToLower` and the distance is computed on the lowered strings.
   If false, the comparison is case-sensitive.
4. The function is pure: no side effects, safe for concurrent use.

Examples:

| `s` | `t` | `ignoreCase` | result |
|---|---|---|---|
| `"time"` | `"times"` | true | 1 |
| `"tiems"` | `"times"` | true | 2 |
| `"tims"` | `"times"` | true | 1 |
| `"timeS"` | `"times"` | true | 0 |
| `"timeS"` | `"times"` | false | 1 |
| `"rimes"` | `"times"` | true | 1 |
| `"ti"` | `"times"` | true | 3 |
| `"timely"` | `"times"` | true | 2 |
| `"ri"` | `"times"` | true | 4 |
| `"timezone"` | `"times"` | true | 4 |
| `"foo"` | `"times"` | true | 5 |
| `"kitten"` | `"sitting"` | false | 3 |
| `""` | `"abc"` | false | 3 |
| `"abc"` | `""` | false | 3 |
| `""` | `""` | true | 0 |

## 3. Input specification

- `s`, `t`: arbitrary Go strings (any bytes, possibly empty, possibly
  non-ASCII UTF-8). Lengths may reach a few thousand bytes.
- `ignoreCase`: whether to lower-case both strings first.

## 4. Output specification

- An `int` in the range `[max(len(a),len(b)) - min(len(a),len(b)), max(len(a),len(b))]`,
  where `a` and `b` are the (possibly lower-cased) strings that are compared and
  `len` is the length in bytes.
- `0` exactly when the compared strings are identical.
- Symmetric: `ld(s, t, x) == ld(t, s, x)`.

## 5. Edge cases and constraints

- Either or both strings empty: the result is the byte length of the other
  one (after optional lower-casing).
- With `ignoreCase`, lower-casing may change the byte length of some
  non-ASCII characters; the distance is always computed on the lowered
  strings.
- Never panics, never returns a negative number.
