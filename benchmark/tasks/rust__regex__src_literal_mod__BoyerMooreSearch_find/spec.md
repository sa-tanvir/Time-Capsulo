# Functional specification: `BoyerMooreSearch::find(&self, haystack: &[u8]) -> Option<usize>`

## 1. Component overview

Part of the literal-search layer of the `regex` crate. When a regular expression begins with (or consists
of) a single literal byte string, the crate uses a pre-compiled single-substring searcher to jump to
candidate match positions quickly. `BoyerMooreSearch` is one such searcher; it is built once per needle
(`BoyerMooreSearch::new(pattern)`, which fills in the instance state described in `context.md`) and then
`find` is called on many haystacks. `find` must return exactly what a plain substring search returns; the
pre-computed tables only exist to make it fast.

## 2. Functional requirements

1. Return `Some(i)` where `i` is the **smallest** byte offset such that
   `haystack[i .. i + pattern.len()] == pattern[..]` (the leftmost occurrence), or `None` if the pattern does
   not occur in `haystack`.
2. Matching is exact, byte-wise, case-sensitive; bytes are arbitrary (`0x00`–`0xFF`, not necessarily UTF-8).
3. Occurrences may overlap other partial occurrences; only the start offset of the first complete occurrence
   matters (e.g. pattern `"abab"` in `"abaababab"` gives `Some(3)`).
4. If `haystack.len() < pattern.len()`, return `None`.
5. The result must be correct for every haystack length, including haystacks only slightly longer than the
   pattern and haystacks whose occurrence sits at the very end.

Examples:

| pattern | haystack | result |
|---|---|---|
| `b"pattern"` | `b"I keep seeing patterns in this text"` | `Some(14)` |
| `b"pattern"` | `b"I keep seeing needles in this text"` | `None` |
| `[0,1,1,0]` | `[0,0,0,0,0,1,1,0]` | `Some(4)` |
| `[0,0]` | `[0,0]` | `Some(0)` |
| `[91]` | `[91]` | `Some(0)` |
| `[1,1,1,1,32,32,87]` | 98 bytes (all `0` except a single `87` at offset 27) followed by the pattern | `Some(98)` |
| `b"clone_created"` | `"// "` + 32×`a` + `"\ne_data.clone_created(entity_id, …"` | `Some(43)` |
| `[1,1,1,1,1,1,1]` | 86 zero bytes | `None` (must not panic) |
| any non-empty `p` | `p ++ p` | `Some(0)` |

Property: for every non-empty pattern and haystack the result equals a naive left-to-right scan, and equals
the result of `FreqyPacked::new(pattern).find(haystack)` (the other single-substring searcher in this file).

## 3. Input specification

- `self`: a searcher created by `BoyerMooreSearch::new(pattern)` with a **non-empty** pattern (any length,
  any bytes). The instance state is read-only; see `context.md`.
- `haystack: &[u8]`: any length, including 0.

## 4. Output specification

- `Option<usize>`: start offset (in bytes, 0-based) of the leftmost occurrence, or `None`.

## 5. Edge cases and constraints

- Must never panic or index out of bounds, whatever the relation between haystack and pattern lengths
  (pattern equal in length to the haystack, occurrence at offset 0 or ending at the last byte, haystack of
  repeated bytes, haystack with no byte of the pattern at all).
- `&self` is not modified; the method is safe to call concurrently from several threads.
- Expected to be fast on long haystacks (tens to hundreds of KB) with patterns of 1–64 bytes, including
  adversarial inputs with many near-miss occurrences (a single byte differs).
- For a one-byte pattern `md2_shift` holds a meaningless sentinel and must not be relied upon.
