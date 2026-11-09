You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `expand_str(caps: &re_unicode::Captures, replacement: &str, dst: &mut String)`

## 1. Component overview

Internal helper of the `regex` crate behind `Captures::expand` and the `$`-template replacers used by
`Regex::replace`, `replace_all` and `replacen`. Given the capture groups of one match and a replacement
template, it **appends** to `dst` the template with every capture reference replaced by the text of the
referenced group.

## 2. Functional requirements

1. Scan `replacement` from left to right. Text that is not part of a `$` construct is appended to `dst`
   unchanged (including any non-ASCII characters).
2. `$$` appends a single literal `$` and scanning resumes after the two characters (so `$$1` yields `$1`
   and `$$$$` yields `$$`).
3. Any other `$` starts a capture reference, parsed exactly as `find_cap_ref` does (see `context.md`):
   `$NAME` takes the **longest** run of ASCII letters, digits and `_` after the `$`; `${NAME}` takes the
   run inside braces and requires the closing `}`. A NAME that parses as a `u32` is a group **index**
   (`$0` is the whole match, `$007` is group 7); any other NAME (including numbers too large for `u32`)
   is a group **name**.
4. For a valid reference, append the text of that group in `caps` (`caps.get(index)` or `caps.name(name)`).
   If the group does not exist, or exists but did not participate in the match, append nothing (the empty
   string). Then continue right after the reference (after the `}` for the braced form).
5. If the `$` does not start a valid reference (e.g. `$` at the end, `$ `, `$-`, `$é`, `${`, `${}`,
   `${a b}`, `${42`), append a literal `$` and continue with the character right after that `$`
   (so `"${a"` with group `a`="abc" yields `"${a"`, and `"$"` yields `"$"`).
6. Existing contents of `dst` are kept; output is appended at its end.

Examples (`caps` from `(?P<a>\w+)\s+(?P<b>\d+)` on `"abc 123"`):

| replacement | appended to `dst` |
|---|---|
| `"$b$a"` | `"123abc"` |
| `".$b.$a."` | `".123.abc."` |
| `" $b $a "` | `" 123 abc "` |
| `"z$bz$az"` | `"z"` (groups `bz`, `az` do not exist) |
| `"$bz$az"` | `""` |

Other examples: with `(?P<foo>\w+)` on `"abc"`: `"$foo"`, `"$0"`, `"$1"` all give `"abc"`; `"$$1"` gives
`"$1"`; `"$$foo"` gives `"$foo"`; `"${foo}bar$foobar"` gives `"abcbar"`. With `(.)` on `"b"`: `"${1}a $1a"` gives
`"ba "`. With `(\S+)\s+(\S+)` on `"w1 w2"`: `"$2 $1"` gives `"w2 w1"`, `"$2 $$1"` gives `"w2 $1"`.
With `(\w) (\w)?` on `"a "` (group 2 unmatched): `"[$2|$1]"` gives `"[|a]"`.

## 3. Input specification

- `caps: &re_unicode::Captures`: the capture groups of one successful match (group 0 always present).
- `replacement: &str`: any template text, possibly empty, possibly containing non-ASCII characters.
- `dst: &mut String`: output buffer; may already contain text.

## 4. Output specification

- No return value; the expansion is appended to `dst`. `caps` and `replacement` are not modified.

## 5. Edge cases and constraints

- Empty `replacement` appends nothing; a template with no `$` is appended verbatim.
- Must never panic for any template, and must only split the template at ASCII positions, so the output
  is always valid UTF-8.
- Work should be linear in `replacement.len()` plus the total length of the inserted group texts; long
  literal runs between `$` signs should be copied in bulk (templates can be tens of KB).

=== CONTEXT ===
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
expand_bytes caps : & re_bytes :: Captures , mut replacement : & [ u8 ] , dst : & mut Vec < u8 > ,
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
- `re_unicode::Captures<'t>`: `get(&self, i: usize) -> Option<Match<'t>>` (None if group `i` does not exist or did
  not participate), `name(&self, name: &str) -> Option<Match<'t>>` (same for named groups); `Match::as_str()`.
- `memchr(needle: u8, haystack: &[u8]) -> Option<usize>`: index of the first occurrence of a byte.

=== STUB ===
```rust
pub fn expand_str(
    caps: &re_unicode::Captures,
    mut replacement: &str,
    dst: &mut String,
) {
    // TODO: implement according to the specification
}
```
