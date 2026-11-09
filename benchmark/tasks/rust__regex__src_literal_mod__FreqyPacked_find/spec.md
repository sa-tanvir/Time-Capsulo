# Functional specification: `FreqyPacked::find(&self, haystack: &[u8]) -> Option<usize>`

## 1. Component overview

Part of the literal-search layer of the `regex` crate. When a regex starts with a single literal byte
string (its longest common prefix or suffix, or a lone literal), the crate searches for that literal with
`FreqyPacked`, a single-substring searcher built once per needle by `FreqyPacked::new(pat)` that records
the needle's two rarest bytes (according to a fixed, pre-computed byte-frequency ranking) so that the scan
can stay inside the very fast `memchr` routine. `find` is called on many haystacks and must return exactly
what a plain substring search returns.

## 2. Functional requirements

1. If the pattern is empty, return `None` (not `Some(0)`).
2. If `haystack.len() < pat.len()`, return `None`.
3. Otherwise return `Some(i)` where `i` is the **smallest** byte offset with
   `haystack[i .. i + pat.len()] == pat[..]` (leftmost occurrence), or `None` if there is no occurrence.
4. Matching is exact and byte-wise over arbitrary bytes (`0x00`–`0xFF`).
5. Overlapping partial occurrences do not matter; only the first complete occurrence counts
   (pattern `"abab"` in `"abaababab"` gives `Some(3)`; `"aaaa"` in `"aaaaaaaaaa"` gives `Some(0)`).

Examples:

| pattern | haystack | result |
|---|---|---|
| `b"pattern"` | `b"I keep seeing patterns in this text"` | `Some(14)` |
| `b"pattern"` | `b"I keep seeing needles in this text"` | `None` |
| `[0,1,1,0]` | `[0,0,0,0,0,1,1,0]` | `Some(4)` |
| `b"abc"` | `b"ab"` | `None` |
| `b"abc"` | `b"xabcabc"` | `Some(1)` |
| `b"a"` | `b"bbbbbbbba"` | `Some(8)` |
| `b""` | `b"abc"` | `None` |

Property: for every non-empty pattern the result equals a naive left-to-right scan, and equals
`BoyerMooreSearch::new(pat).find(haystack)`. Through the public API this is what makes, for example,
`Regex::new("abc").find("xxabc")` report the match at 2..5 and `Regex::new("^foo").replace_all("foobar", "")`
give `"bar"`; a wrong offset breaks literal-prefix, suffix and Unicode-literal matching throughout the crate.

## 3. Input specification

- `self`: built by `FreqyPacked::new(pat)` (any bytes, possibly empty); read-only, see `context.md`.
- `haystack: &[u8]`: any length, including 0.

## 4. Output specification

- `Option<usize>`: 0-based byte offset of the start of the leftmost occurrence, or `None`.

## 5. Edge cases and constraints

- Must never panic: candidate positions near the end of the haystack, where the whole pattern would not
  fit, simply do not match.
- `&self` is not modified; safe to call concurrently.
- Expected to be fast on haystacks of tens to hundreds of KB, including inputs where the rare bytes are in
  fact common, and inputs with many near-miss occurrences (one byte altered).
