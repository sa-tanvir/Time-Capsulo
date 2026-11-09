# Context for the function to implement

- **Language:** rust
- **File:** `src/expand.rs`

## Imports / includes available in this file

```
use std::str;
use memchr::memchr;
use re_bytes;
use re_unicode;
    use super::{CaptureRef, find_cap_ref};
```

## Other functions defined in the same file (signatures only; you may call them)

```
expand_str caps : & re_unicode :: Captures , mut replacement : & str , dst : & mut String ,
find_cap_ref replacement : & T ,
from x : & a str
from x : usize
is_valid_cap_letter b : & u8
```

## Related items

- `find_cap_ref(replacement: &T) -> Option<CaptureRef>` (same file, `T: ?Sized + AsRef<[u8]>`): parses one capture
  reference that must start at byte 0 of its argument (`$name`, `$7`, `${name}`); returns `None` if there is none
  (input shorter than 2 bytes, first byte not `$`, empty name, or missing `}`). `CaptureRef { cap: Ref, end: usize }`
  where `end` is the byte offset just past the reference, and `enum Ref<'a> { Named(&'a str), Number(usize) }`
  (`Number` when the name parses as `u32`).
- `re_bytes::Captures<'t>`: `get(&self, i: usize) -> Option<Match<'t>>` (None if group `i` does not exist or did
  not participate), `name(&self, name: &str) -> Option<Match<'t>>` (same for named groups); `Match::as_bytes()`.
- `memchr(needle: u8, haystack: &[u8]) -> Option<usize>`: index of the first occurrence of a byte.
