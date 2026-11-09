You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Regex::replacen(&self, text: &'t str, limit: usize, rep: R) -> Cow<'t, str>`

## 1. Component overview

Public method of `regex::Regex` (Unicode / `&str` API). It replaces at most `limit` successive
non-overlapping matches of the regex in `text` with a replacement produced by `rep`, which implements the
`Replacer` trait (see `context.md`): a `&str` template with `$name`/`$1`/`${name}` capture references, a
`NoExpand(&str)` literal, or a closure `FnMut(&Captures) -> String`. `replace(text, rep)` is
`replacen(text, 1, rep)` and `replace_all(text, rep)` is `replacen(text, 0, rep)`.

## 2. Functional requirements

1. The matches considered are exactly those yielded, in order, by `self.find_iter(text)` (equivalently the
   group-0 spans of `self.captures_iter(text)`): leftmost-first, non-overlapping, including empty matches
   with the iterator's usual rules for them.
2. `limit == 0` means "replace every match"; otherwise only the first `limit` matches are replaced and the
   rest of the text (including later matches) is copied unchanged.
3. Output = the text before the first replaced match, then its replacement, then the text between that
   match's end and the next replaced match's start, its replacement, and so on, then all text after the
   last replaced match. Non-matching text is copied verbatim.
4. What is inserted for a match:
   - If `rep.no_expansion()` returns `Some(s)` (a `&str` template containing no `$`, or any `NoExpand`),
     insert `s` for every replaced match. `no_expansion` should be asked once per call.
   - Otherwise call `rep.replace_append(&caps, &mut out)` once per replaced match, in match order, with the
     `Captures` of that match; it appends the replacement. For a `&str` template this performs `$`
     expansion (`$1`, `$name`, `${name}`, `$$` → `$`; references to missing groups expand to ""). For a
     closure, the closure is invoked exactly once for each replaced match and **never** for matches beyond
     the limit.
5. If the regex has **no match at all** in `text`, return `Cow::Borrowed(text)` (no allocation, and a
   closure replacer is never called). Whenever at least one match exists, return `Cow::Owned(new_string)`
   (even if the replacement happens to reproduce the original text).

Examples (from the crate's tests):

| regex | text | call | result |
|---|---|---|---|
| `\d` | `"age: 26"` | `replace(…, "Z")` | `"age: Z6"` |
| `\d+` | `"age: 26"` | `replace(…, "Z")` | `"age: Z"` |
| `\d` | `"age: 26"` | `replace_all(…, "Z")` | `"age: ZZ"` |
| `(\S+)\s+(\S+)` | `"w1 w2"` | `replace(…, "$2 $1")` | `"w2 w1"` |
| `(\S+)\s+(\S+)` | `"w1 w2"` | `replace(…, "$2 $$1")` | `"w2 $1"` |
| `(?P<first>\S+)\s+(?P<last>\S+)(?P<space>\s*)` | `"w1 w2 w3 w4"` | `replace_all(…, "$last $first$space")` | `"w2 w1 w4 w3"` |
| `^[ \t]+\|[ \t]+$` | `" \t  trim me\t   \t"` | `replace_all(…, "")` | `"trim me"` |
| `(.)(.)` | `"ab"` | `replace(…, "$1-$2")` | `"a-b"` |
| `(\w+) (\w+)` | `"a b"` | `replace_all(…, "$2 $$c $1")` | `"b $c a"` |
| `(\S+)\s+(\S+)` | `"w1 w2"` | `replace(…, NoExpand("$2 $1"))` | `"$2 $1"` |
| `(\S+)\s+(\S+)` | `"w1 w2"` | `replace(…, NoExpand("$$1"))` | `"$$1"` |
| `foo` | `"foobar"` | `replace_all(…, "")` | `"bar"` |
| `^` | `"bar"` | `replace(…, "foo")` | `"foobar"` |
| `(.)` | `"b"` | `replace_all(…, "${1}a $1a")` | `"ba "` (`$1a` names a missing group) |

## 3. Input specification

- `self`: a compiled `Regex`.
- `text: &'t str`: any UTF-8 text, possibly empty.
- `limit: usize`: maximum number of replacements; `0` = unlimited.
- `rep: R` where `R: Replacer` (taken by value; may be stateful, e.g. a counting closure).

## 4. Output specification

- `Cow<'t, str>`: `Borrowed(text)` iff there is no match; otherwise `Owned` with the new string.

## 5. Edge cases and constraints

- Empty text: `Borrowed("")` unless the regex matches the empty string (e.g. `^` or `x*`), in which case the
  replacement is inserted.
- Matches are never overlapping and are processed strictly left to right; slices are taken on match
  boundaries, which always lie on UTF-8 character boundaries.
- `self` is not modified; `text` is not modified.
- Should not do needless work: when `no_expansion` gives a fixed string, capture groups need not be
  resolved, and the output can be pre-sized from `text.len()`.

=== CONTEXT ===
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

=== STUB ===
```rust
pub fn replacen<'t, R: Replacer>(
    &self,
    text: &'t str,
    limit: usize,
    mut rep: R,
) -> Cow<'t, str> {
    // TODO: implement according to the specification
}
```
