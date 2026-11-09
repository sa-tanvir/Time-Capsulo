# Functional specification: `generic_damerau_levenshtein(a_elems, b_elems) -> usize`

## 1. Component overview

Part of `strsim`, a library of string-similarity metrics.
`generic_damerau_levenshtein` returns the **(unrestricted)
Damerau–Levenshtein distance** between two slices: the minimum number of
insertions, deletions, substitutions and transpositions of adjacent elements
needed to turn `a_elems` into `b_elems`, where — unlike optimal string
alignment — substrings may be edited any number of times, so the triangle
inequality holds. The crate's `damerau_levenshtein(&str, &str)` collects both
strings into `char` vectors and calls this function, and
`normalized_damerau_levenshtein` divides that result by the longer `char`
length; their tested values therefore depend on it.

## 2. Functional requirements

1. Return the minimum total cost to transform `a_elems` into `b_elems` using
   these operations, each costing 1:
   - insert one element,
   - delete one element,
   - substitute one element by a different one,
   - transpose two adjacent elements.
2. Edits may overlap: e.g. two elements may be transposed and then have other
   elements inserted between them, each step costing its own unit. This is the
   true edit distance under the four operations.
3. Element equality is `Eq` equality; elements are opaque values otherwise.

Examples (strings via `damerau_levenshtein`, compared by `char`):

| `a` | `b` | result |
|---|---|---|
| `""` | `""` | `0` |
| `"damerau"` | `"damerau"` | `0` |
| `""` | `"damerau"` | `7` |
| `"damerau"` | `""` | `7` |
| `"ca"` | `"abc"` | `2` |
| `"ac"` | `"cba"` | `2` |
| `"ab"` | `"bca"` | `2` |
| `"damerau"` | `"aderua"` | `3` (same reversed) |
| `"damerau"` | `"aderuaxyz"` | `6` (same reversed) |
| `"öঙ香"` | `"abc"` | `3` (same reversed) |
| `"Stewart"` | `"Colbert"` | `5` |
| `"abcdefghijkl"` | `"bacedfgihjlk"` | `4` |
| `"foobar"` | `"ofobar"` | `1` |
| `"specter"` | `"spectre"` | `1` |
| `"a cat"` | `"an abct"` | `3` |
| `"The quick brown fox jumped over the angry dog."` | `"Lehem ipsum dolor sit amet, dicta latine an eam."` | `36` |

Generic: `generic_damerau_levenshtein(&[1,2], &[2,3,1])` is `2`.
`normalized_damerau_levenshtein("levenshtein", "löwenbräu")` ≈ `0.27272`
(distance 8 over length 11).

## 3. Input specification

- `a_elems: &[Elem]`, `b_elems: &[Elem]` with `Elem: Eq + Hash + Clone`
  (both slices have the same element type). Lengths from 0 to a few thousand.
- Running time roughly proportional to `len(a) * len(b)` is expected; memory
  proportional to that product is acceptable.

## 4. Output specification

A `usize` distance, `0 <= d <= max(len(a), len(b))`. The slices are not
modified; no side effects.

## 5. Edge cases and constraints

- `a_elems` empty → `len(b_elems)`; `b_elems` empty → `len(a_elems)`.
- Equal slices → `0`.
- The result is symmetric in its arguments and satisfies the triangle
  inequality.
- Must not panic for any inputs (including repeated elements and slices made
  of a single repeated value).
