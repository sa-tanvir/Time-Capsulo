# Context for the function to implement

- **Language:** rust
- **File:** `src/re_bytes.rs`
- **Enclosing scope:** `impl Regex`

## Imports / includes available in this file

```
use std::borrow::Cow;
use std::collections::HashMap;
use std::fmt;
use std::ops::Index;
use std::str::FromStr;
use std::sync::Arc;
use memchr::memchr;
use exec::{Exec, ExecNoSync};
use expand::expand_bytes;
use error::Error;
use re_builder::bytes::RegexBuilder;
use re_trait::{self, RegularExpression, Locations, SubCapturesPosIter};
            use std::ascii::escape_default;
```

## Other functions defined in the same file (signatures only; you may call them)

```
as_bytes & self
as_str & self
by_ref & r mut self
capture_names & self
captures & self , text : & t [ u8 ]
captures_iter & r self , text : & t [ u8 ] ,
captures_len & self
end & self
escape_byte byte : u8
escape_bytes bytes : & [ u8 ]
expand & self , replacement : & [ u8 ] , dst : & mut Vec < u8 >
find & self , text : & t [ u8 ]
find_at & self , text : & t [ u8 ] , start : usize ,
find_iter & r self , text : & t [ u8 ]
fmt & self , f : & mut fmt :: Formatter
from exec : Exec
from_str s : & str
get & self , i : usize
index & a self , name : & i str
index & self , i : usize
is_match & self , text : & [ u8 ]
is_match_at & self , text : & [ u8 ] , start : usize
iter & c self
len & self
locations & self
name & self , name : & str
new haystack : & t [ u8 ] , start : usize , end : usize
new re : & str
next & mut self
no_expansion & mut self
no_expansion & r mut self
read_captures_at & self , locs : & mut Locations , text : & t [ u8 ] , start : usize ,
replace & self , text : & t [ u8 ] , rep : R ,
replace_all & self , text : & t [ u8 ] , rep : R ,
replace_append & mut self , _ : & Captures , dst : & mut Vec < u8 >
replace_append & mut self , caps : & Captures , dst : & mut Vec < u8 >
shortest_match & self , text : & [ u8 ]
shortest_match_at & self , text : & [ u8 ] , start : usize ,
size_hint & self
split & r self , text : & t [ u8 ]
splitn & r self , text : & t [ u8 ] , limit : usize ,
start & self
```

## Related public API (same module, `regex::bytes`)

```rust
pub trait Replacer {
    /// Appends the replacement for the current match (`caps` always has group 0) to `dst`.
    fn replace_append(&mut self, caps: &Captures, dst: &mut Vec<u8>);
    /// A fixed replacement if no capture access is needed; default `None`.
    fn no_expansion<'r>(&'r mut self) -> Option<Cow<'r, [u8]>> { None }
    fn by_ref<'r>(&'r mut self) -> ReplacerRef<'r, Self> { .. }
}
// impl Replacer for &'a [u8]       : replace_append = caps.expand(self, dst); no_expansion = Some(self) iff self has no b'$'
// impl Replacer for NoExpand<'t>   : (NoExpand(pub &'t [u8])) replace_append extends with self.0; no_expansion = Some(self.0)
// impl<F: FnMut(&Captures) -> Vec<u8>> Replacer for F : replace_append extends with the closure's result; no_expansion = None
```

- `self.find_iter(text)` -> iterator of `Match<'t>` (`start()`, `end()`, `as_bytes()`), successive non-overlapping matches.
- `self.captures_iter(text)` -> iterator of `Captures<'t>`; `caps.get(0).unwrap()` is the whole match.
