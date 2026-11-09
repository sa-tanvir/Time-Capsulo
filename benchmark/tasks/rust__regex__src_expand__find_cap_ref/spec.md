# Functional specification: `find_cap_ref(replacement: &T) -> Option<CaptureRef>`

## 1. Component overview

Part of the `regex` crate's replacement-string expansion (used by `Captures::expand`, `Regex::replace`,
`replace_all`, `replacen`). In a replacement template, `$name`, `$3` or `${name}` refers to a capture group.
`find_cap_ref` parses **one** such reference that must begin at the very first byte of `replacement`, and
reports which group it names and where the reference ends. It does not handle the `$$` escape (callers
deal with that before calling it).

## 2. Functional requirements

1. View `replacement` as bytes (`replacement.as_ref()`).
2. If the input has length 0 or 1, or its first byte is not `$`, return `None`.
3. After the `$` there are two forms:
   - **Bare form** `$NAME`: NAME is the longest run (possibly empty) of *capture-name bytes* starting right
     after the `$`. Capture-name bytes are exactly ASCII `0-9`, `a-z`, `A-Z` and `_`.
   - **Braced form** `${NAME}`: if the byte right after `$` is `{`, NAME is the longest run of capture-name
     bytes after the `{`, and it must be followed immediately by `}`.
4. If NAME is empty, return `None` (e.g. `"$ x"`, `"${}"`, `"$-1"`).
5. In the braced form, if the byte after NAME is not `}` (including end of input), return `None`
   (e.g. `"${42"`, `"${42 "`, `"${a-b}"`).
6. Otherwise return `Some(CaptureRef { cap, end })`:
   - `cap` is `Ref::Number(n)` if NAME parses as a decimal `u32` (`str::parse::<u32>`), with `n` that value
     as `usize`; otherwise `cap` is `Ref::Named(NAME)` where NAME is a `&str` borrowing the input bytes.
     So `"$007"` gives `Number(7)`; `"$4294967295"` gives `Number(4294967295)`; `"$4294967296"`
     (exceeds `u32`) and `"$42a"` give `Named`.
   - `end` is the byte offset just past the reference: past the last NAME byte in the bare form, past the
     closing `}` in the braced form.
7. Matching is greedy: a bare name absorbs every following capture-name byte, so `"$1a"` is `Named("1a")`
   rather than group 1 followed by `a`; use braces to delimit (`"${1}a"` is `Number(1)` with `end` 4).
   Bytes after the reference (anything, including non-UTF-8 or non-ASCII) are ignored.

Examples (`c!(x, e)` = `Some(CaptureRef { cap: x.into(), end: e })`):

| input | result |
|---|---|
| `"$foo"` | `Named("foo")`, end 4 |
| `"${foo}"` | `Named("foo")`, end 6 |
| `"$0"` | `Number(0)`, end 2 |
| `"$5"` | `Number(5)`, end 2 |
| `"$10"` | `Number(10)`, end 3 |
| `"$42a"` | `Named("42a")`, end 4 |
| `"${42}a"` | `Number(42)`, end 5 |
| `"$first_"` | `Named("first_")`, end 7 |
| `"${42"`, `"${42 "`, `" $0 "`, `"$"`, `" "`, `""` | `None` |

In context (through `replace`/`expand`): with groups `a="abc"`, `b="123"`, template `"$b$a"` gives
`"123abc"`, `".$b.$a."` gives `".123.abc."`, `"z$bz$az"` gives `"z"` (names `bz`, `az` do not exist and
expand to empty), `"${1}a $1a"` on a single-char match `b` gives `"ba "`, `"$1-$2"` gives `"a-b"`.

## 3. Input specification

- `replacement: &T` where `T: ?Sized + AsRef<[u8]>` — in practice `&str` or `&[u8]`; arbitrary bytes,
  any length (including empty). Bytes outside the reference need not be valid UTF-8.

## 4. Output specification

- `Option<CaptureRef<'_>>` as defined in `context.md`, borrowing from `replacement` for `Ref::Named`.
- `None` when no valid reference starts at offset 0.

## 5. Edge cases and constraints

- Pure function: no allocation of owned output is required, no mutation, no panics for any input.
- Names may be arbitrarily long (thousands of bytes); numeric names too long for `u32` are `Named`.
- A leading `+` or `-` is not a capture-name byte, so `"$+1"` is `None`.
- Only the first reference is parsed; `"${a}}"` gives `Named("a")`, end 4.
