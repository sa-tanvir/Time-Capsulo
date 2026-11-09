You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `generic_hamming(a, b) -> HammingResult`

## 1. Component overview

Part of `strsim`, a library of string-similarity metrics. `generic_hamming`
computes the **Hamming distance** between two sequences of arbitrary element
types: the number of positions at which the corresponding elements differ.
The string convenience wrapper `hamming(a: &str, b: &str)` (already present in
the crate) calls this function with `a.chars()` and `b.chars()`, so its
behaviour is fully determined by this function.

## 2. Functional requirements

1. Walk both sequences in lock-step, position by position, from the start.
2. For every position where both sequences have an element, compare the pair
   with `!=` (the bound `Elem1: PartialEq<Elem2>`); count the positions where the
   elements are **not equal**.
3. If both sequences end at the same position (equal lengths), return
   `Ok(count)`.
4. If one sequence ends before the other (different lengths), return
   `Err(StrSimError::DifferentLengthArgs)`. No partial count is returned.
5. Each input is consumed at most once (single pass); inputs that are one-shot
   iterators must work.

Examples (via `hamming`, which compares Unicode scalar values / `char`s):

| `a` | `b` | result |
|---|---|---|
| `""` | `""` | `Ok(0)` |
| `"hamming"` | `"hamming"` | `Ok(0)` |
| `"hamming"` | `"hammers"` | `Ok(3)` |
| `"hamming"` | `"h香mmüng"` | `Ok(2)` (multibyte chars count as one element each) |
| `"Friedrich Nietzs"` | `"Jean-Paul Sartre"` | `Ok(14)` |
| `"ham"` | `"hamming"` | `Err(DifferentLengthArgs)` |

Generic example: `generic_hamming(&[1, 2, 4], &[1, 2, 3])` is `Ok(1)`
(slices of integers iterate by reference).

## 3. Input specification

- `a: Iter1`, `b: Iter2` — any values implementing `IntoIterator`, taken by
  value. Element types may differ (`Elem1`, `Elem2`) as long as
  `Elem1: PartialEq<Elem2>`.
- Sequences may be empty and may be very long (millions of elements); the
  function must run in time linear in the sequence length and need no extra
  memory proportional to the input.

## 4. Output specification

`HammingResult`, i.e. `Result<usize, StrSimError>`:

- `Ok(n)` with `0 <= n <= len` where `len` is the common length.
- `Err(StrSimError::DifferentLengthArgs)` when lengths differ. (`StrSimError`
  displays as `"Differing length arguments provided"`; that formatting already
  exists and is not part of this function.)

## 5. Edge cases and constraints

- Two empty inputs: `Ok(0)`.
- One empty, the other non-empty: `Err(DifferentLengthArgs)`, regardless of
  which argument is the shorter one.
- Different lengths are an error even when the shared prefix is identical.
- The function is pure: no global state, no panics for any input, and it
  does not modify anything other than consuming the iterators it was given.

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/lib.rs`
- **Enclosing scope:** `impl Error for StrSimError {}`

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
pub fn generic_hamming<Iter1, Iter2, Elem1, Elem2>(a: Iter1, b: Iter2) -> HammingResult
    where Iter1: IntoIterator<Item=Elem1>,
          Iter2: IntoIterator<Item=Elem2>,
          Elem1: PartialEq<Elem2> {
    // TODO: implement according to the specification
}
```
