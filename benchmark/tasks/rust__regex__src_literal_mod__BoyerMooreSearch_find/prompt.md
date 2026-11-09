You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/literal/mod.rs`
- **Enclosing scope:** `impl BoyerMooreSearch`

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

## Instance state (`struct BoyerMooreSearch`, filled by `BoyerMooreSearch::new(pattern)`; read-only here)

| field | type | meaning |
|---|---|---|
| `pattern` | `Vec<u8>` | the needle; always non-empty |
| `skip_table` | `Vec<usize>` (256 entries) | indexed by a byte `b`: `pattern.len()` if `b` does not occur in `pattern`, otherwise `pattern.len() - 1 - j` where `j` is the index of the **last** occurrence of `b` in `pattern` (so the pattern's last byte maps to `0`) |
| `guard` | `u8` | the rarest byte of `pattern` according to the crate's fixed byte-frequency ranking (first such byte on ties; `pattern[0]` if none is rarer) |
| `guard_reverse_idx` | `usize` | `pattern.len() - 1 - j` where `j` is the index of `guard` chosen above |
| `md2_shift` | `usize` | if the last pattern byte also occurs at some index `1 <= i <= len-2`, then `len - 1 - i` for the largest such `i`; otherwise `len - 1`. For `len == 1` it is the sentinel `0xDEADBEAF` |

Sibling methods you may call: `self.len() -> usize` (pattern length),
`self.check_match(haystack: &[u8], window_end: usize) -> bool` (true iff the pattern occurs ending exactly at
index `window_end`, i.e. `haystack[window_end + 1 - len ..= window_end] == pattern`; requires
`window_end + 1 >= len` and `window_end < haystack.len()`), and
`self.skip_loop(haystack, window_end, backstop) -> Option<usize>` (internal helper of the original
implementation; you need not use it). `memchr::memchr(byte, slice) -> Option<usize>` is imported.

=== STUB ===
```rust
fn find(&self, haystack: &[u8]) -> Option<usize> {
    // TODO: implement according to the specification
}
```
