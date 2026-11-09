You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `osa_distance(a: &str, b: &str) -> usize`

## 1. Component overview

Part of `strsim`, a library of string-similarity metrics. `osa_distance`
computes the **Optimal String Alignment** distance (also called the
*restricted* Damerau–Levenshtein distance) between two strings: like the
Levenshtein distance, but a swap of two **adjacent** characters also counts as
a single edit — with the restriction that no substring may be edited more than
once.

## 2. Functional requirements

1. Operate on the strings as sequences of Unicode scalar values (`char`s),
   not bytes. A multibyte character is one element.
2. Return the minimum number of edits turning `a` into `b`, each costing 1:
   - insert a character,
   - delete a character,
   - substitute a character by a different one,
   - transpose two adjacent characters (`"ab"` → `"ba"`).
3. **Restriction:** a transposed pair cannot take part in any further edit,
   and no character may be inserted between, or edited inside, a region that
   was already edited. Formally, the result is the classic OSA recurrence:
   `d[i][j]` = minimum of `d[i-1][j]+1`, `d[i][j-1]+1`,
   `d[i-1][j-1]+cost`, and — when `i>1`, `j>1`, `a[i] == b[j-1]`,
   `a[i-1] == b[j]` and `a[i] != b[j]` — `d[i-2][j-2]+1` (1-based `char`
   indices; `cost` is 0 for equal characters, 1 otherwise). Because of this
   restriction the triangle inequality does not hold.

Examples:

| `a` | `b` | result |
|---|---|---|
| `""` | `""` | `0` |
| `"damerau"` | `"damerau"` | `0` |
| `""` | `"damerau"` | `7` |
| `"damerau"` | `""` | `7` |
| `"ab"` | `"bca"` | `3` |
| `"ca"` | `"abc"` | `3` (the unrestricted distance would be 2) |
| `"ac"` | `"cba"` | `3` |
| `"damerau"` | `"aderua"` | `3` (same reversed) |
| `"damerau"` | `"aderuaxyz"` | `6` (same reversed) |
| `"öঙ香"` | `"abc"` | `3` (same reversed) |
| `"Stewart"` | `"Colbert"` | `5` |
| `"abcdefghijkl"` | `"bacedfgihjlk"` | `4` |
| `"foobar"` | `"ofobar"` | `1` |
| `"specter"` | `"spectre"` | `1` |
| `"a cat"` | `"an abct"` | `4` (unrestricted would be 3) |
| `"The quick brown fox jumped over the angry dog."` | `"Lehem ipsum dolor sit amet, dicta latine an eam."` | `36` |

## 3. Input specification

- `a`, `b`: arbitrary UTF-8 string slices, possibly empty, up to a few
  thousand characters each.
- Running time proportional to `chars(a) * chars(b)` is expected; extra memory
  should be proportional to the length of one string, not the product.

## 4. Output specification

A `usize` distance with `0 <= d <= max(chars(a), chars(b))`. Inputs are not
modified; no side effects.

## 5. Edge cases and constraints

- Identical strings → `0`.
- One string empty → the `char` count of the other.
- The result is symmetric in its arguments.
- A transposition is only recognised for two adjacent characters that are
  different from each other (`"aa"` vs `"aa"` is simply equal).
- Must not panic for any input, including strings made only of multibyte
  characters.

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
pub fn osa_distance(a: &str, b: &str) -> usize {
    // TODO: implement according to the specification
}
```
