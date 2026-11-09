# Functional specification

## 1. Component overview

`lexer::scan()` is the tokenizer step of the JSON parser: it reads the next token from the lexer's input and returns its kind (`token_type`). It skips insignificant whitespace, recognises the structural characters, delegates literals, strings and numbers to the specialised scanning routines, and signals the end of the input and malformed input.

## 2. Functional requirements

1. **Byte order mark.** At the very beginning of the input (when no character has been read yet, i.e. `position.chars_read_total == 0`), an optional UTF-8 byte order mark (bytes `EF BB BF`) is skipped. If the input starts with `0xEF` that is not followed by `0xBB 0xBF`, the call fails: `error_message` is set to `invalid BOM; must be 0xEF 0xBB 0xBF if given` and `token_type::parse_error` is returned. The BOM check is only made at the start of the input, never later, and a BOM is accepted once.
2. **Whitespace.** The next character is read; space (`0x20`), horizontal tab (`0x09`), line feed (`0x0A`) and carriage return (`0x0D`) are skipped (repeatedly). No other character counts as whitespace (e.g. vertical tab, form feed and non-breaking space are not skipped).
3. The first non-whitespace character decides the token (the character is consumed as part of the token):
   - `[` returns `begin_array`, `]` returns `end_array`, `{` returns `begin_object`, `}` returns `end_object`, `:` returns `name_separator`, `,` returns `value_separator`.
   - `t` starts the literal `true` (token `literal_true`), `f` the literal `false` (`literal_false`), `n` the literal `null` (`literal_null`). The whole literal text must follow; otherwise the result is `parse_error` with `error_message` = `invalid literal`.
   - `"` starts a string: the rest of the string is scanned and the result is `value_string` or `parse_error`.
   - `-` or a digit `0`-`9` starts a number: the number is scanned and the result is `value_unsigned`, `value_integer` or `value_float`, or `parse_error`.
   - The NUL character (`0x00`) and the end of the input both return `end_of_input` (NUL is treated like the end of the input).
   - Any other character returns `parse_error` with `error_message` = `invalid literal`.

## 3. Input specification

The lexer reads bytes from its input source (a string, stream or buffer). No argument. The function may be called repeatedly; each call continues after the previous token. Calling it again after `end_of_input` or an error is outside the contract.

## 4. Output specification

Returns the `token_type` of the next token. For `value_string`, `value_unsigned`, `value_integer` and `value_float`, the value is stored in the lexer for later retrieval by the scanning routines (not by this function). After a successful token the input position (`position.chars_read_total`) is directly behind the last character of the token (for numbers the scanning routine handles the one-character look-ahead). `error_message` is set only when `parse_error` is returned by this function itself (the two messages above); the scanning routines set their own messages.

## 5. Edge cases and constraints

- Empty input, or input consisting only of whitespace, returns `end_of_input`.
- `  [ 1` returns `begin_array` first; calling again returns `value_unsigned` (the `1`).
- `true` returns `literal_true`; `tru` and `trux` return `parse_error` ("invalid literal"); `truex` returns `literal_true` first (the following `x` is read by the next call and gives `parse_error`, "invalid literal").
- A BOM followed by text: `EF BB BF 5B` returns `begin_array`; a lone `EF`, or `EF BB` without the third byte, or `EF BB BD`, returns `parse_error` (invalid BOM message). A BOM that appears after other characters (e.g. after a space or after another token) is an ordinary invalid character: `parse_error` with `invalid literal`.
- A NUL byte in the middle of the input ends the token stream: the call that reaches it returns `end_of_input`.
- A character such as `#`, `'`, `/`, `+`, `.`, a letter other than `t`, `f`, `n`, or a byte >= 0x80 outside a string gives `parse_error` with `invalid literal`.
