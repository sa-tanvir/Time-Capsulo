# Functional specification: `func tostr(json string) (raw string, str string)`

## 1. Component overview

`tostr` is an internal helper of the `gjson` package (`github.com/tidwall/gjson`),
which extracts values from JSON text without fully decoding it. It is called when
the parser reaches a JSON string literal: `json` is the remainder of a document,
starting at the opening `"`. `tostr` returns the raw text of the literal (as it
appears in the document) and its decoded value. `Parse` and the array/object
member listing (`Result.Array`, `Result.Map`, `Result.Value`) use it to fill in
`Result.Raw` and `Result.Str` for string values.

## 2. Functional requirements

Let the *closing quote* be the first `"` after the opening one that is preceded
by an **even** number (including zero) of consecutive backslashes. (A quote
preceded by an odd number of backslashes is escaped and belongs to the string.)

1. **No backslash before the closing quote.** If a closing quote is found and
   there is no `\` between the opening and the closing quote:
   - `raw` = the input up to and including the closing quote;
   - `str` = the characters between the two quotes, copied **verbatim** (no
     decoding; control characters such as a literal tab are kept).
2. **No backslash and no closing quote.** `raw` = the whole input and `str` =
   the whole input without its first character.
3. **Backslash present.** If a `\` occurs before the closing quote (or before
   the end of the input when there is no closing quote):
   - Let `end` be the index of the closing quote, or `len(json)` when there is
     none.
   - `str` = `unescape(json[1:end])`, i.e. the content between the opening quote
     and `end`, decoded exactly as the `unescape` function in the context does
     (decoding stops early at a raw control character, an unknown escape, or a
     truncated `\u` escape).
   - `raw` = `json[:end+1]` (through the closing quote) **if** there is at least
     one more character after the closing quote; otherwise (the closing quote is
     the very last character of the input, or there is no closing quote)
     `raw` = `json[:end]`. In other words, in the escaped case a closing quote
     that ends the input is *not* included in `raw`.
4. Text after the closing quote is ignored. The function is pure and safe for
   concurrent use; it never panics for inputs that meet section 3.

## 3. Input specification

- `json`: a Go string of length >= 1 whose first byte is `"`. The rest is
  arbitrary bytes (normally JSON string content, possibly with `\uXXXX`
  escapes, raw UTF-8, and trailing document text such as `,`, `]`, `}`).

## 4. Output specification

- `raw`: always a prefix of `json` (starting with the opening quote).
- `str`: the decoded string value as described above (valid or invalid UTF-8
  is passed through unchanged in the verbatim case; `\u` escapes are encoded as
  UTF-8, lone surrogates become U+FFFD as done by `unescape`).

## 5. Edge cases and constraints

Inputs and outputs below are shown as raw text; `<TAB>` is a literal tab byte.

| `json` | `raw` | `str` |
|---|---|---|
| `"hello"` | `"hello"` | `hello` |
| `"hello",1` | `"hello"` | `hello` |
| `""` | `""` | (empty) |
| `"",` | `""` | (empty) |
| `"abc` | `"abc` | `abc` |
| `"a<TAB>b"x` | `"a<TAB>b"` | `a<TAB>b` |
| `"中文",` | `"中文"` | `中文` |
| `"a\"b",` | `"a\"b"` | `a"b` |
| `"a\"b"` | `"a\"b` (final quote dropped) | `a"b` |
| `"\\"x` | `"\\"` | `\` |
| `"x\\\"y"z` | `"x\\\"y"` | `x\"y` |
| `"été"}` | `"été"` | `été` |
| `"😀"]` | `"😀"` | `😀` |
| `"\ud83d"]` | `"\ud83d"` | U+FFFD |
| `"\/\b\f\r\t"` | `"\/\b\f\r\t` | `/`, backspace, form feed, CR, tab |
| `"ab\ncd` | `"ab\ncd` | `ab`, newline, `cd` |
| `"a<TAB>b\n"` | `"a<TAB>b\n` | `a` (decoding stops at the raw tab) |
| `"bad\q"x` | `"bad\q"` | `bad` (unknown escape stops decoding) |
| `"\u12"` | `"\u12` | (empty: truncated `\u` escape) |
| `"\` | `"\` | (empty) |
| `"\"` | `"\"` | `"` (no closing quote) |
| `"q\\"` | `"q\\` | `q\` |

- Runs in time linear in the length of the string literal.
