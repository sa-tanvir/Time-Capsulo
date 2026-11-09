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
