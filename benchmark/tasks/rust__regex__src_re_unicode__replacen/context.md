# Context for the function to implement

- **Language:** rust
- **File:** `src/re_unicode.rs`
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
use syntax;
use error::Error;
use exec::{Exec, ExecNoSyncStr};
use expand::expand_str;
use re_builder::unicode::RegexBuilder;
use re_trait::{self, RegularExpression, Locations, SubCapturesPosIter};
```

## Other functions defined in the same file (signatures only; you may call them)

```
as_str & self
by_ref & r mut self
capture_names & self
captures & self , text : & t str
captures_iter & r self , text : & t str ,
captures_len & self
end & self
escape text : & str
expand & self , replacement : & str , dst : & mut String
find & self , text : & t str
find_at & self , text : & t str , start : usize ,
find_iter & r self , text : & t str
fmt & self , f : & mut fmt :: Formatter
from exec : Exec
from m : Match < t >
from_str s : & str
get & self , i : usize
index & a self , name : & i str
index & self , i : usize
is_match & self , text : & str
is_match_at & self , text : & str , start : usize
iter & c self
len & self
locations & self
name & self , name : & str
new haystack : & t str , start : usize , end : usize
new re : & str
next & mut self
no_expansion & mut self
read_captures_at & self , locs : & mut Locations , text : & t str , start : usize ,
replace & self , text : & t str , rep : R ,
replace_all & self , text : & t str , rep : R ,
replace_append & mut self , _ : & Captures , dst : & mut String
replace_append & mut self , caps : & Captures , dst : & mut String
shortest_match & self , text : & str
shortest_match_at & self , text : & str , start : usize ,
size_hint & self
split & r self , text : & t str
splitn & r self , text : & t str , limit : usize
start & self
```

## Related public API (same crate)

```rust
pub trait Replacer {
    /// Appends the replacement for the current match (`caps` always has group 0) to `dst`.
    fn replace_append(&mut self, caps: &Captures, dst: &mut String);
    /// A fixed replacement string if no capture access is needed; default `None`.
    fn no_expansion<'r>(&'r mut self) -> Option<Cow<'r, str>> { None }
    fn by_ref<'r>(&'r mut self) -> ReplacerRef<'r, Self> { .. }
}
// impl Replacer for &'a str        : replace_append = caps.expand(self, dst); no_expansion = Some(self) iff self has no '$'
// impl Replacer for NoExpand<'t>   : replace_append pushes self.0; no_expansion = Some(self.0)
// impl<F: FnMut(&Captures) -> String> Replacer for F : replace_append pushes the closure's result; no_expansion = None
```

- `self.find_iter(text)` -> iterator of `Match<'t>` (`start()`, `end()`, `as_str()`), successive non-overlapping matches.
- `self.captures_iter(text)` -> iterator of `Captures<'t>`; `caps.get(0).unwrap()` is the whole match.
