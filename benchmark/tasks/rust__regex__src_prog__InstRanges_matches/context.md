# Context for the function to implement

- **Language:** rust
- **File:** `src/prog.rs`
- **Enclosing scope:** `impl InstRanges`

## Imports / includes available in this file

```
use std::collections::HashMap;
use std::cmp::Ordering;
use std::fmt;
use std::ops::Deref;
use std::mem;
use std::slice;
use std::sync::Arc;
use input::Char;
use literal::LiteralSearcher;
        use self::Inst::*;
            use std::ascii::escape_default;
```

## Other functions defined in the same file (signatures only; you may call them)

```
approximate_size & self
deref & self
fmt & self , f : & mut fmt :: Formatter
into_iter self
is_match & self
leads_to_match & self , pc : usize
matches & self , byte : u8
needs_dotstar & self
new
num_chars & self
only_utf8 & self
skip & self , mut pc : usize
uses_bytes & self
visible_byte b : u8
with_goto cur : usize , goto : usize , fmtd : String
```

## Instance state (`pub struct InstRanges`)

| field | type | meaning |
|---|---|---|
| `goto` | `InstPtr` (`usize`) | next instruction on success (not used by `matches`) |
| `ranges` | `Vec<(char, char)>` | the class: inclusive `(start, end)` scalar-value ranges, sorted ascending, non-overlapping |

Sibling: `num_chars(&self) -> usize` (total number of characters covered).

## `input::Char` (imported)

`pub struct Char(u32)` — `#[derive(Clone, Copy, Hash, PartialEq, Eq, PartialOrd, Ord)]`. Holds a Unicode scalar
value, or `u32::MAX` meaning "absent" (no character, e.g. at the end of the input). `Char::from(c: char)`,
`Char::from(None::<char>)` (absent), `c.is_none()`. It implements `PartialEq<char>` and `PartialOrd<char>`
(and the reverse), comparing the raw `u32` values, so the absent value compares greater than every `char`.
`std::cmp::Ordering` is imported.
