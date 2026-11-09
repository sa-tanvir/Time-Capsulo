# Functional specification: `bytes::Regex::replacen(&self, text: &'t [u8], limit: usize, rep: R) -> Cow<'t, [u8]>`

## 1. Component overview

Public method of `regex::bytes::Regex` (byte-slice API: haystacks are `&[u8]`, not necessarily UTF-8). It replaces at most `limit` successive
non-overlapping matches of the regex in `text` with a replacement produced by `rep`, which implements the
`Replacer` trait (see `context.md`): a `&[u8]` template with `$name`/`$1`/`${name}` capture references, a
`NoExpand(&[u8])` literal (`regex::bytes::NoExpand`), or a closure `FnMut(&Captures) -> Vec<u8>`. `replace(text, rep)` is
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
   - If `rep.no_expansion()` returns `Some(s)` (a `&[u8]` template containing no `$` byte, or any `NoExpand`),
     insert `s` for every replaced match. `no_expansion` should be asked once per call.
   - Otherwise call `rep.replace_append(&caps, &mut out)` once per replaced match, in match order, with the
     `Captures` of that match; it appends the replacement. For a `&[u8]` template this performs `$`
     expansion (`$1`, `$name`, `${name}`, `$$` → `$`; references to missing groups expand to ""). For a
     closure, the closure is invoked exactly once for each replaced match and **never** for matches beyond
     the limit.
5. If the regex has **no match at all** in `text`, return `Cow::Borrowed(text)` (no allocation, and a
   closure replacer is never called). Whenever at least one match exists, return `Cow::Owned(new_bytes)`
   (even if the replacement happens to reproduce the original text).

Examples (from the crate's tests; text and templates are byte strings, e.g. `b"age: 26"`):

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
- `text: &'t [u8]`: arbitrary bytes (may contain invalid UTF-8), possibly empty.
- `limit: usize`: maximum number of replacements; `0` = unlimited.
- `rep: R` where `R: Replacer` (taken by value; may be stateful, e.g. a counting closure).

## 4. Output specification

- `Cow<'t, [u8]>`: `Borrowed(text)` iff there is no match; otherwise `Owned` with the new bytes.

## 5. Edge cases and constraints

- Empty text: `Borrowed(b"")` unless the regex matches the empty string (e.g. `^` or `x*`), in which case the
  replacement is inserted.
- Matches are never overlapping and are processed strictly left to right; bytes outside matches (including
  invalid UTF-8) are copied verbatim.
- `self` is not modified; `text` is not modified.
- Should not do needless work: when `no_expansion` gives a fixed string, capture groups need not be
  resolved, and the output can be pre-sized from `text.len()`.
