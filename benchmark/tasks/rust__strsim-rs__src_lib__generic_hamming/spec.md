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
