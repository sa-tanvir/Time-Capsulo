# Functional specification

## 1. Component overview

`StringUtil.appendNormalisedWhitespace(accum, string, stripLeading)` appends a whitespace-normalised copy of `string` to the `StringBuilder` `accum`, the way jsoup normalises text for `Element.text()`: runs of whitespace collapse to a single space and invisible formatting characters are dropped.

## 2. Functional requirements

Process `string` code point by code point (a surrogate pair is one code point). Existing content of `accum` is left untouched; output is only appended.

1. **Whitespace code points** are exactly: space, tab (`\t`), line feed, form feed, carriage return, and U+00A0 (non-breaking space). (`StringUtil.isActuallyWhitespace(int)` tests this.) A maximal run of whitespace code points produces a single `' '` (U+0020) in the output, regardless of which whitespace characters it contains.
2. **Invisible code points** are U+200B, U+200C, U+200D (zero-width space, non-joiner, joiner) and U+00AD (soft hyphen). (`StringUtil.isInvisibleChar(int)` tests this.) They are never appended. They are transparent to the whitespace logic: they neither end a whitespace run nor count as visible content. So `"a ​ b"` yields `"a b"`.
3. **Every other code point** is appended unchanged (including supplementary code points, and characters such as U+2003 or vertical tab that are not in the whitespace set above). Appending one ends the current whitespace run and marks that visible content has been seen.
4. **`stripLeading`**: if true, whitespace that occurs before the first visible (appended, non-whitespace) code point is dropped entirely. If false, leading whitespace becomes a single space. Trailing whitespace is never stripped: it becomes a single trailing space.
5. The run collapsing is measured on the output, not the input: whitespace separated only by invisible code points counts as one run.

## 3. Input specification

`accum`: a non-null `StringBuilder` (may already hold text). `string`: a non-null `String` of any length, possibly empty, containing any Unicode text. `stripLeading`: a boolean.

## 4. Output specification

Returns nothing (`void`); the result is appended to `accum`. Examples (appended text):
- `("  a \t b  ", false)` appends `" a b "`; with `stripLeading = true` it appends `"a b "`.
- `("  x", true)` appends `"x"`; with `false` appends `" x"`.
- `("a​b", *)` appends `"ab"`.
- `("x  y", *)` appends `"x y"`.
- `("​  ‍ a", true)` appends `"a"`.
- `("", *)` or a string of only invisible characters appends nothing.

## 5. Edge cases and constraints

- Surrogate pairs must be kept intact (do not split them).
- No locale or time dependence; the function does not modify `string` and is not thread-safe with respect to `accum`.
