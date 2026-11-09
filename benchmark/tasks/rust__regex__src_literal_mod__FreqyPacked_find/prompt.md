You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/literal/mod.rs`
- **Enclosing scope:** `impl FreqyPacked`

## Imports / includes available in this file

```
use std::cmp;
use std::mem;
use aho_corasick::{Automaton, AcAutomaton, FullAcAutomaton};
use memchr::{memchr, memchr2, memchr3};
use syntax::hir::literal::{Literal, Literals};
use freqs::BYTE_FREQUENCIES;
use self::teddy_avx2::{Teddy as TeddyAVX2};
use self::teddy_ssse3::{Teddy as TeddySSSE3};
        use self::Matcher::*;
        use self::Matcher::*;
        use self::Matcher::*;
        use std::mem;
    use super::{BoyerMooreSearch, FreqyPacked};
    use quickcheck::TestResult;
```

## Other functions defined in the same file (signatures only; you may call them)

```
_find & self , haystack : & [ u8 ]
approximate_size & self
bm_backstop_boundary
bm_backstop_underflow_bug
bm_find_no_subs
bm_find_subs
bm_memchr_fallback_indexing_bug
bm_naive_off_by_one_bug
bm_skip_reset_bug
bm_win_gnu_indexing_bug
char_len & self
char_len_lossy bytes : & [ u8 ]
check_match & self , haystack : & [ u8 ] , window_end : usize
compile_md2_shift pattern : & [ u8 ]
compile_skip_table pattern : & [ u8 ]
complete & self
empty
find & self , haystack : & [ u8 ]
find & self , text : & [ u8 ]
find_end & self , haystack : & [ u8 ]
find_start & self , haystack : & [ u8 ]
freq_rank b : u8
is_empty & self
is_suffix & self , text : & [ u8 ]
iter & self
lcp & self
lcs & self
len & self
naive_find needle : & [ u8 ] , haystack : & [ u8 ]
new
new lits : & Literals , sset : SingleByteSet
new lits : Literals , matcher : Matcher
new pat : Vec < u8 >
new pattern : Vec < u8 >
next & mut self
prefixes lits : & Literals
prefixes lits : Literals
qc_bm_equals_nieve_find pile1 : Vec < u8 > , pile2 : Vec < u8 >
qc_bm_equals_single pile1 : Vec < u8 > , pile2 : Vec < u8 >
qc_bm_finds_first needle : Vec < u8 >
qc_bm_finds_subslice haystack : Vec < u8 > , needle_start : usize , needle_length : usize
qc_bm_finds_trailing_needle haystack_pre : Vec < u8 > , needle : Vec < u8 >
select_guard pattern : & [ u8 ]
should_use pattern : & [ u8 ]
skip_loop & self , haystack : & [ u8 ] , mut window_end : usize , backstop : usize ,
suffixes lits : & Literals
suffixes lits : Literals
```

## Instance state (`struct FreqyPacked`, filled by `FreqyPacked::new(pat)`; read-only here)

| field | type | meaning |
|---|---|---|
| `pat` | `Vec<u8>` | the needle (may be empty) |
| `char_len` | `usize` | number of Unicode characters in `pat` (lossy decoding); not needed for searching |
| `rare1` | `u8` | the rarest byte of `pat` according to the crate's fixed byte-frequency ranking |
| `rare1i` | `usize` | index of the **last** occurrence of `rare1` in `pat` |
| `rare2` | `u8` | the second-rarest byte of `pat` (distinct from `rare1` when `pat` has at least two distinct bytes, otherwise equal to it) |
| `rare2i` | `usize` | index of the last occurrence of `rare2` in `pat` |

For an empty pattern all of `rare1`, `rare1i`, `rare2`, `rare2i`, `char_len` are `0`.
Invariant for non-empty patterns: `pat[rare1i] == rare1` and `pat[rare2i] == rare2`.
Sibling methods: `self.len() -> usize` (pattern length), `self.is_suffix(text) -> bool`, `self.char_len()`.
`memchr::memchr(byte, slice) -> Option<usize>` is imported.

=== STUB ===
```rust
pub fn find(&self, haystack: &[u8]) -> Option<usize> {
    // TODO: implement according to the specification
}
```
