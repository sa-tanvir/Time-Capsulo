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
