You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `generic_levenshtein(a, b) -> usize`

## 1. Component overview

Part of `strsim`, a library of string-similarity metrics.
`generic_levenshtein` returns the **Levenshtein edit distance** between two
sequences: the minimum number of single-element insertions, deletions and
substitutions needed to turn `a` into `b`. The crate's
`levenshtein(&str, &str)` calls it on the strings' `char` sequences and
`normalized_levenshtein` divides that result by the longer `char` length, so
their tested values depend on this function.

## 2. Functional requirements

1. Return the minimum total number of edit operations transforming `a` into
   `b`, where each of the following costs exactly 1:
   - insert one element,
   - delete one element,
   - replace one element by a different one.
   Matching an element with an equal element costs 0. Equality is decided with
   `==` through the bound `Elem1: PartialEq<Elem2>`.
2. Elements are compared as whole sequence items: for strings (via
   `levenshtein`) that means Unicode scalar values (`char`), not bytes.
3. The result is a true metric value: `0` iff the sequences are equal, and
   equal to the other sequence's length when one sequence is empty.

Examples (strings via `levenshtein`):

| `a` | `b` | result |
|---|---|---|
| `""` | `""` | `0` |
| `"levenshtein"` | `"levenshtein"` | `0` |
| `"kitten"` | `"sitting"` | `3` |
| `"hello, world"` | `"bye, world"` | `5` |
| `"öঙ香"` | `"abc"` | `3` (and `3` reversed) |
| `""` | `"sitting"` | `7` |
| `"kitten"` | `""` | `6` |
| `"The quick brown fox jumped over the angry dog."` | `"Lorem ipsum dolor sit amet, dicta latine an eam."` | `37` |

Generic: `generic_levenshtein(&[1,2,3], &[1,2,3,4,5,6])` is `3`.
`normalized_levenshtein("kitten", "sitting")` ≈ `0.57142` follows from `3/7`.

## 3. Input specification

- `a: &'a Iter1`, `b: &'b Iter2`, where `&Iter1: IntoIterator<Item = Elem1>`,
  `&Iter2: IntoIterator<Item = Elem2>` and `Elem1: PartialEq<Elem2>`. The
  references can be iterated as many times as needed (e.g. `&Vec<char>`,
  `&[i32; 3]`, or the crate's internal string wrapper).
- Lengths range from 0 to a few thousand elements. Memory use should be
  proportional to the length of one input (not the product of both lengths);
  running time proportional to `len(a) * len(b)` is expected.

## 4. Output specification

A `usize` distance, `0 <= d <= max(len(a), len(b))`. The inputs are not
modified; the function has no side effects.

## 5. Edge cases and constraints

- `a` empty → return `len(b)`; `b` empty → return `len(a)`; both empty → `0`.
- The result is symmetric (`d(a,b) == d(b,a)`) for same-typed inputs.
- A swap of two adjacent elements costs 2 (no transposition operation).
- Must not panic or overflow for any lengths in the stated range.

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
generic_damerau_levenshtein a_elems : & [ Elem ] , b_elems : & [ Elem ]
generic_hamming a : Iter1 , b : Iter2
generic_jaro a : & 'a Iter1, b: &' b Iter2
generic_jaro_diff
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
pub fn generic_levenshtein<'a, 'b, Iter1, Iter2, Elem1, Elem2>(a: &'a Iter1, b: &'b Iter2) -> usize
    where &'a Iter1: IntoIterator<Item=Elem1>,
          &'b Iter2: IntoIterator<Item=Elem2>,
          Elem1: PartialEq<Elem2> {
    // TODO: implement according to the specification
}
```
