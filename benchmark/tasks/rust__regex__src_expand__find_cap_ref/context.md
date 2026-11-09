# Context for the function to implement

- **Language:** rust
- **File:** `src/expand.rs`
- **Enclosing scope:** free function (module level)

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
expand_bytes caps : & re_bytes :: Captures , mut replacement : & [ u8 ] , dst : & mut Vec < u8 > ,
expand_str caps : & re_unicode :: Captures , mut replacement : & str , dst : & mut String ,
from x : & a str
from x : usize
is_valid_cap_letter b : & u8
```

## Types defined in this file (used by the signature)

```rust
/// A reference to a capture group inside some text, tagged with the position
/// in the text immediately following the reference.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct CaptureRef<'a> {
    cap: Ref<'a>,
    end: usize,
}

/// A reference to a capture group, e.g. `$2`, `$foo`, `${foo}`.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Ref<'a> {
    Named(&'a str),
    Number(usize),
}
// impl From<&'a str> for Ref<'a>  (-> Ref::Named)
// impl From<usize> for Ref<'static> (-> Ref::Number)
```

`is_valid_cap_letter(b: &u8) -> bool` returns true exactly for ASCII `0-9`, `a-z`, `A-Z` and `_`.
