# Functional specification: `expand_bytes(caps: &re_bytes::Captures, replacement: &[u8], dst: &mut Vec<u8>)`

## 1. Component overview

Internal helper of the `regex` crate behind `bytes::Captures::expand` and the `$`-template replacers used by
`bytes::Regex::replace`, `replace_all` and `replacen`. Given the capture groups of one match and a replacement
template, it **appends** to `dst` the template with every capture reference replaced by the text of the
referenced group.

## 2. Functional requirements

1. Scan `replacement` from left to right. Bytes that are not part of a `$` construct are appended to `dst`
   unchanged (including non-ASCII and invalid UTF-8 bytes).
2. `$$` appends a single literal `$` and scanning resumes after the two characters (so `$$1` yields `$1`
   and `$$$$` yields `$$`).
3. Any other `$` starts a capture reference, parsed exactly as `find_cap_ref` does (see `context.md`):
   `$NAME` takes the **longest** run of ASCII letters, digits and `_` after the `$`; `${NAME}` takes the
   run inside braces and requires the closing `}`. A NAME that parses as a `u32` is a group **index**
   (`$0` is the whole match, `$007` is group 7); any other NAME (including numbers too large for `u32`)
   is a group **name**.
4. For a valid reference, append the text of that group in `caps` (`caps.get(index)` or `caps.name(name)`, as bytes).
   If the group does not exist, or exists but did not participate in the match, append nothing (the empty
   string). Then continue right after the reference (after the `}` for the braced form).
5. If the `$` does not start a valid reference (e.g. `$` at the end, `$ `, `$-`, `$é`, `${`, `${}`,
   `${a b}`, `${42`), append a literal `$` and continue with the byte right after that `$`
   (so `"${a"` with group `a`="abc" yields `"${a"`, and `"$"` yields `"$"`).
6. Existing contents of `dst` are kept; output is appended at its end.

Examples (byte strings; `caps` from `(?P<a>\w+)\s+(?P<b>\d+)` on `"abc 123"`):

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

- `caps: &re_bytes::Captures`: the capture groups of one successful match (group 0 always present).
- `replacement: &[u8]`: any template bytes, possibly empty, possibly invalid UTF-8.
- `dst: &mut Vec<u8>`: output buffer; may already contain bytes.

## 4. Output specification

- No return value; the expansion is appended to `dst`. `caps` and `replacement` are not modified.

## 5. Edge cases and constraints

- Empty `replacement` appends nothing; a template with no `$` is appended verbatim.
- Must never panic for any template; bytes following a `$` that are not name bytes (e.g. `0xFF`) are
  ordinary literal bytes.
- Work should be linear in `replacement.len()` plus the total length of the inserted group texts; long
  literal runs between `$` signs should be copied in bulk (templates can be tens of KB).
