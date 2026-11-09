# Functional specification: `parse_arg_id(begin, end, handler)`

## 1. Component overview

Part of the format-string parser of the fmt library. It parses the *argument id* that follows the `{` of a replacement field: nothing (automatic numbering), a decimal index (`{0}`, `{12:x}`) or an identifier naming an argument (`{name}`, `{width:>5}`). The result is reported to a handler through callbacks and the function returns the position after the id.

## 2. Functional requirements

The range `[begin, end)` is the text that follows the opening brace; it is never empty. Let `c` be its first character.

1. **No id.** If `c` is `}` or `:`, call `handler()` (the call with no arguments) and return `begin` (nothing is consumed).
2. **Numeric id.** If `c` is a decimal digit, parse an index from the digits with `parse_nonnegative_int` (a leading `0` is a whole number by itself, so `0` is index 0 and in `01` only the `0` is the number). Number-too-big errors are reported by that helper to the handler's `on_error`. Afterwards:
   - if the number is followed by the end of the range, or by a character that is neither `}` nor `:`, call `handler.on_error("invalid format string")`;
   - otherwise call `handler(index)` with the parsed `int`.
   In both cases return the position directly after the digits (the position of the `}` or `:`, or of the offending character).
3. **Named id.** If `c` is a letter (`a`-`z`, `A`-`Z`) or `_`, the name is the longest prefix made of letters, digits and `_`. Call `handler(basic_string_view<Char>(begin, length))` with exactly that prefix and return the position after the name. No check is made on what follows the name (it may be the end of the range).
4. **Anything else** (any other first character, e.g. `-`, a space, `{`, a non-ASCII character): call `handler.on_error("invalid format string")` and return `begin`.

Exactly one handler call is made, except that a number that is too big first triggers `on_error("number is too big")` from the helper (which does not return in practice).

## 3. Input specification

- `begin`, `end`: `const Char*` with `begin != end`.
- `handler`: as described in the context. `on_error` is assumed not to return (it throws); behaviour after it returns is not tested.

## 4. Output specification

Returns the pointer to the first character after the parsed id, as described above. The function itself throws nothing; errors go through `handler.on_error`.

## 5. Edge cases and constraints

| text | handler call | returned offset |
|---|---|---|
| `}` , `:x` | `handler()` | 0 |
| `0}` | `handler(0)` | 1 |
| `12:>5` | `handler(12)` | 2 |
| `2147483647}` | `handler(2147483647)` | 10 |
| `2147483648}` | `on_error("number is too big")` | |
| `01}` | `on_error("invalid format string")` | 1 |
| `5x}` | `on_error("invalid format string")` | 1 |
| `7` | `on_error("invalid format string")` | 1 |
| `name}` | `handler("name")` | 4 |
| `_a1:x` | `handler("_a1")` | 3 |
| `abc` | `handler("abc")` | 3 |
| `9a}` | `on_error("invalid format string")` | 1 |
| `-1}` , ` }` , `{}` | `on_error("invalid format string")` | 0 |
