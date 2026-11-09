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
