# Functional specification: `InstRanges::matches(&self, c: Char) -> bool`

## 1. Component overview

Part of the `regex` crate's compiled program representation. A Unicode character class such as `[a-z]`,
`\w`, `\pL` or `[^\n]` compiles (in the Unicode, non-byte programs used by the PikeVM and backtracking
engines) to a `Ranges` instruction, represented by `InstRanges`. During matching the engines call
`matches` once per input character to decide whether the character belongs to the class, so it is on a
very hot path (classes may contain thousands of ranges, while most text is ASCII).

## 2. Functional requirements

1. Return `true` iff `c` is a present character whose scalar value `v` satisfies `lo <= v <= hi` for at
   least one `(lo, hi)` in `self.ranges` (both bounds inclusive).
2. The "absent" character (`Char::from(None)`, used at the end of the input; see `context.md`) never
   matches any range; return `false` for it.
3. `self.ranges` is sorted in ascending order and the ranges do not overlap (see §3); the result for a
   character must be correct whether it falls inside a range, exactly on a bound, in a gap between two
   ranges, below the first range or above the last one.
4. An empty `ranges` vector matches nothing.

Examples (ranges written as code points):

| ranges | c | result |
|---|---|---|
| `[('a','z')]` | `'a'`, `'m'`, `'z'` | `true` |
| `[('a','z')]` | `'`'` (U+0060), `'{'` (U+007B), absent | `false` |
| `[(U+0,U+2), (U+4,U+6)]` | U+3, U+7 | `false` |
| `[(U+0,U+2), (U+4,U+6)]` | U+0, U+4, U+6 | `true` |
| `[('0','9'), ('A','Z'), ('_','_'), ('a','z')]` | `'_'` | `true` |
| same | `'@'`, `'é'` | `false` |
| `[(U+0, U+10FFFF)]` | any present character | `true` |
| `[(U+2028, U+2029)]` | U+2029 | `true` |

Through the public API, `matches` decides e.g. whether `\w` matches `"é"`, whether `[^a]` matches `"b"`,
or whether `\p{Zl}` matches U+2028, in every Unicode regex executed by the NFA or backtracking engines.

## 3. Input specification

- `self.ranges: Vec<(char, char)>`: inclusive ranges with `lo <= hi`, sorted ascending, non-overlapping
  (`hi_i < lo_{i+1}`); length 0 to several thousand. `self.goto` is irrelevant here.
- `c: Char`: a Unicode scalar value or the absent character (see `context.md`).

## 4. Output specification

- `bool`: membership of `c` in the union of the ranges.

## 5. Edge cases and constraints

- Must not panic for any `c` (including the absent value) or any valid `ranges`.
- `&self` is not modified; safe for concurrent use.
- Expected to be fast both for small classes queried with ASCII text and for large classes (thousands of
  ranges), i.e. better than a linear scan over all ranges for large classes.
