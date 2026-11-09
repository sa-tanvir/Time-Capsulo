You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/lib.rs`

## Imports / includes available in this file

```
use std::char;
use std::cmp::{max, min};
use std::collections::HashMap;
use std::error::Error;
use std::fmt::{self, Display, Formatter};
use std::hash::Hash;
use std::str::Chars;
    use super::*;
```

## Other functions defined in the same file (signatures only; you may call them)

```
assert_hamming_dist dist : usize , str1 : & str , str2 : & str
damerau_levenshtein a : & str , b : & str
damerau_levenshtein_beginning_transposition
damerau_levenshtein_diff
damerau_levenshtein_diff_comedians
damerau_levenshtein_diff_longer
damerau_levenshtein_diff_multibyte
damerau_levenshtein_diff_reversed
damerau_levenshtein_diff_short
damerau_levenshtein_diff_unequal_length
damerau_levenshtein_diff_unequal_length_reversed
damerau_levenshtein_empty
damerau_levenshtein_end_transposition
damerau_levenshtein_first_empty
damerau_levenshtein_many_transpositions
damerau_levenshtein_same
damerau_levenshtein_second_empty
damerau_levenshtein_unrestricted_edit
flat_index i : usize , j : usize , width : usize
fmt & self , fmt : & mut Formatter
generic_hamming a : Iter1 , b : Iter2
generic_jaro a : & 'a Iter1, b: &' b Iter2
generic_jaro_diff
generic_levenshtein a : & 'a Iter1, b: &' b Iter2
hamming a : & str , b : & str
hamming_diff
hamming_diff_multibyte
hamming_empty
hamming_names
hamming_numbers
hamming_same
hamming_unequal_length
jaro_both_empty
jaro_diff_no_transposition
jaro_diff_one_and_two
jaro_diff_one_character
jaro_diff_short
jaro_diff_two_and_one
jaro_diff_with_transposition
jaro_first_empty
jaro_multibyte
jaro_names
jaro_same
jaro_second_empty
jaro_winkler a : & str , b : & str
jaro_winkler_both_empty
jaro_winkler_diff_no_transposition
jaro_winkler_diff_one_character
jaro_winkler_diff_short
jaro_winkler_diff_with_transposition
jaro_winkler_first_empty
jaro_winkler_length_of_one
jaro_winkler_long_prefix
jaro_winkler_more_names
jaro_winkler_multibyte
jaro_winkler_names
jaro_winkler_same
jaro_winkler_second_empty
jaro_winkler_very_long_prefix
levenshtein a : & str , b : & str
levenshtein_diff_longer
levenshtein_diff_multibyte
levenshtein_diff_short
levenshtein_diff_with_space
levenshtein_empty
levenshtein_first_empty
levenshtein_same
levenshtein_second_empty
normalized_damerau_levenshtein a : & str , b : & str
normalized_damerau_levenshtein_diff_short
normalized_damerau_levenshtein_first_empty
normalized_damerau_levenshtein_for_empty_strings
normalized_damerau_levenshtein_identical_strings
normalized_damerau_levenshtein_second_empty
normalized_levenshtein a : & str , b : & str
normalized_levenshtein_diff_short
normalized_levenshtein_first_empty
normalized_levenshtein_for_empty_strings
normalized_levenshtein_identical_strings
normalized_levenshtein_second_empty
osa_distance a : & str , b : & str
osa_distance_beginning_transposition
osa_distance_diff
osa_distance_diff_comedians
osa_distance_diff_longer
osa_distance_diff_multibyte
osa_distance_diff_reversed
osa_distance_diff_short
osa_distance_diff_unequal_length
osa_distance_diff_unequal_length_reversed
osa_distance_empty
osa_distance_end_transposition
osa_distance_first_empty
osa_distance_many_transpositions
osa_distance_restricted_edit
osa_distance_same
osa_distance_second_empty
```

=== STUB ===
```rust
pub fn generic_damerau_levenshtein<Elem>(a_elems: &[Elem], b_elems: &[Elem]) -> usize
    where Elem: Eq + Hash + Clone {
    // TODO: implement according to the specification
}
```
