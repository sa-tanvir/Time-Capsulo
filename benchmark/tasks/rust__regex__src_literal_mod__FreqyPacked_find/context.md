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
