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
