# Functional specification: `parse_align(begin, end, handler)`

## 1. Component overview

Part of the format-string parser of the fmt library. It parses the optional `[[fill]align]` prefix of a standard format specification (for example the `*^` of `{:*^10}` or the `>` of `{:>5}`). It reports what it found to a handler object through callbacks and returns the position after the part it consumed.

## 2. Functional requirements

The range `[begin, end)` is the text of the specification (it is never empty). An *alignment character* is one of `<` (left), `>` (right), `^` (center) and `=` (numeric); they map to `align::left`, `align::right`, `align::center` and `align::numeric` respectively.

1. If the range has at least two characters and the **second** character is an alignment character, the **first** character is a fill character (any character, including another alignment character). The function calls `handler.on_fill(first)` and then `handler.on_align(align)`, and consumes two characters.
2. Otherwise (the range has one character, or its second character is not an alignment character), if the **first** character is an alignment character, the function calls `handler.on_align(align)` once (no `on_fill`) and consumes one character.
3. Otherwise nothing is consumed and no callback is made.
4. Rule 1 has priority over rule 2: for `<<` the fill is `<` and the alignment is left; for `<>` the fill is `<` and the alignment is right; for `x<` the fill is `x`.
5. Exception to rule 1: the fill character `{` is not allowed. When rule 1 applies with first character `{` (for example `{<`, `{^`), the function calls `handler.on_error("invalid fill character '{'")` and returns `begin` (nothing consumed); neither `on_fill` nor `on_align` is called. If `on_error` returns normally, the function still returns `begin`. A lone `{` followed by a non-alignment character is not an error: rule 3 applies. A leading `{` is fine when it is the only alignment-relevant character, e.g. for `{` alone nothing happens.
6. Only the first two characters are ever inspected; the remaining text (width, precision, type, ...) is left untouched.
7. When the character type is wider than `char`, characters are compared to the alignment characters after conversion to `char` (truncation).

## 3. Input specification

- `begin`, `end`: pointers to `Char` with `begin != end` (at least one character).
- `handler`: object with `on_fill`, `on_align` and `on_error` as described in the context.

## 4. Output specification

Returns the pointer to the first character not consumed: `begin`, `begin + 1` or `begin + 2`. Callbacks are made in the order `on_fill` then `on_align`, at most once each. No exceptions are thrown by the function itself (the handler's `on_error` may throw).

## 5. Edge cases and constraints

| text | callbacks | returned offset |
|---|---|---|
| `<` | `on_align(left)` | 1 |
| `*^` | `on_fill('*')`, `on_align(center)` | 2 |
| `*^7` | `on_fill('*')`, `on_align(center)` | 2 |
| `<<` | `on_fill('<')`, `on_align(left)` | 2 |
| `x<y` | `on_fill('x')`, `on_align(left)` | 2 |
| `<x` | `on_align(left)` | 1 |
| `=5` | `on_align(numeric)` | 1 |
| `ab` , `x` , `5` | none | 0 |
| `{<` | `on_error("invalid fill character '{'")` | 0 |
| `{` | none | 0 |

The function is called with every format specification parsed by the library, so it must be fast and must not allocate.
