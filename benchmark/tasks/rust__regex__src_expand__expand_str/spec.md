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
