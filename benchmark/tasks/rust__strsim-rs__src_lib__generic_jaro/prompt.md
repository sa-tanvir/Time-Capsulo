You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `generic_jaro(a, b) -> f64`

## 1. Component overview

Part of `strsim`, a library of string-similarity metrics. `generic_jaro`
computes a **Jaro similarity** score between two sequences, a value in
`[0.0, 1.0]` where `1.0` means identical and `0.0` means nothing in common.
The crate's `jaro(&str, &str)` calls it on the strings' `char` sequences, and
`generic_jaro_winkler` / `jaro_winkler` build on its result (they add a
common-prefix bonus), so their tested values depend on this function.

The exact variant implemented by this crate is defined below; outputs must
match it exactly (up to normal floating-point rounding), including how
"matches" and "transpositions" are counted, which differs from some textbook
descriptions.

## 2. Functional requirements

Let `la` and `lb` be the number of elements of `a` and `b`.

1. **Trivial cases.**
   - `la == 0 && lb == 0` → `1.0`.
   - exactly one of them is `0` → `0.0`.
   - `la == 1 && lb == 1` → `0.0` (even if the two elements are equal).
2. **Search range.** `r = floor(max(la, lb) / 2) - 1` (always `>= 0` once the
   trivial cases are excluded).
3. **Matching.** Process the elements of `a` in order, index `i = 0, 1, ...`.
   Element `a[i]` may match only elements `b[j]` with
   `max(0, i - r) <= j <= min(lb - 1, i + r)`. Among those candidates, `a[i]`
   is matched to the **lowest index `j`** such that `a[i] == b[j]` and `b[j]`
   has not already been matched by an earlier element of `a`. Each `b[j]` can
   be matched at most once; an `a[i]` with no such `j` is unmatched. Let `m` be
   the number of matches.
4. **Transpositions.** Keep track of the `b` index of the most recent match
   (initially `0`). Each time a new match is made at index `j` that is
   **strictly smaller** than the `b` index of the previous match, count one
   transposition. Let `t` be that count (not halved).
5. **Score.** If `m == 0` the result is `0.0`; otherwise
   `(m / la + m / lb + (m - t) / m) / 3`, computed in `f64`.

Examples (through `jaro`, i.e. on `char`s; values rounded to 3 decimals):

| `a` | `b` | result |
|---|---|---|
| `""` | `""` | `1.0` |
| `""` | `"jaro"` | `0.0` |
| `"distance"` | `""` | `0.0` |
| `"jaro"` | `"jaro"` | `1.0` |
| `"a"` | `"b"` | `0.0` |
| `"a"` | `"ab"` | `0.833` (same for `"ab"`, `"a"`) |
| `"dixon"` | `"dicksonx"` | `0.767` |
| `"dwayne"` | `"duane"` | `0.822` |
| `"martha"` | `"marhta"` | `0.944` |
| `"Friedrich Nietzsche"` | `"Jean-Paul Sartre"` | `0.392` |
| `"testabctest"` | `"testöঙ香test"` | `0.818` (either order) |

Generic: `generic_jaro(&[1, 2], &[3, 4])` is `0.0`.

Values that tests derive via `jaro_winkler` (Jaro score `j`, common-prefix
length `p`, result `j + 0.1·p·(1 − j)` capped at 1): e.g. `"cheeseburger"` vs
`"cheese fries"` → `0.911`, `"Dinsdale"` vs `"D"` → `0.738`, `"Thorkel"` vs
`"Thorgier"` → `0.868`, `"dixon"` vs `"dicksonx"` → `0.813` (either order),
`"dwayne"` vs `"duane"` → `0.840`, `"martha"` vs `"marhta"` → `0.961`,
`"Friedrich Nietzsche"` vs `"Fran-Paul Sartre"` → `0.562`,
`"testabctest"` vs `"testöঙ香test"` → `0.89` (either order), and
`"thequickbrownfoxjumpedoverx"` vs `"thequickbrownfoxjumpedovery"` → `1.0`.

## 3. Input specification

- `a: &'a Iter1`, `b: &'b Iter2` where `&Iter1: IntoIterator<Item = Elem1>`
  and `&Iter2: IntoIterator<Item = Elem2>`, with `Elem1: PartialEq<Elem2>`.
  Because the inputs are shared references whose `into_iter()` can be called
  any number of times, the sequences may be traversed more than once
  (e.g. `&Vec<char>`, `&[i32; 2]`, or the crate's internal string wrapper).
- Lengths range from 0 to several thousand elements; elements are compared
  only for equality.

## 4. Output specification

An `f64` in `[0.0, 1.0]` as defined in section 2. The function does not
mutate its inputs and has no side effects.

## 5. Edge cases and constraints

- The single-element pair case returns `0.0` even for equal elements; the
  test suite never relies on the textbook value there.
- The search-range lower bound must never underflow (indices are `usize`).
- Order of arguments matters only through the matching procedure; the
  examples above that are listed "either order" are symmetric, but the
  function is not required to be symmetric in general.
- Must be deterministic and must not panic for any inputs of any lengths.

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
pub fn generic_jaro<'a, 'b, Iter1, Iter2, Elem1, Elem2>(a: &'a Iter1, b: &'b Iter2) -> f64
    where &'a Iter1: IntoIterator<Item=Elem1>,
          &'b Iter2: IntoIterator<Item=Elem2>,
          Elem1: PartialEq<Elem2> {
    // TODO: implement according to the specification
}
```
