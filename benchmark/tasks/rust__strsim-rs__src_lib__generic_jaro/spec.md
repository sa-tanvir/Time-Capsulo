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
