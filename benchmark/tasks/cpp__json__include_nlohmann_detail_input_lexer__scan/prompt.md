You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/nlohmann/detail/input/lexer.hpp` (nlohmann/json 3.7.2), inside `template<typename BasicJsonType> class lexer { ... }` in `namespace nlohmann::detail`.
  Headers available: `<array>`, `<cstdio>`, `<cstring>`, `<string>`, `nlohmann/detail/input/input_adapters.hpp`, `nlohmann/detail/macro_scope.hpp`.
- The stub is a **public non-static member function** of `lexer`; unqualified names below resolve inside the class. `not`, `and`, `or` are the alternative tokens for `!`, `&&`, `||`.

## Types

```
enum class token_type
{
    uninitialized, literal_true, literal_false, literal_null, value_string, value_unsigned, value_integer, value_float,
    begin_array, begin_object, end_array, end_object, name_separator, value_separator, parse_error, end_of_input, literal_or_value
};
struct position_t { std::size_t chars_read_total = 0; std::size_t chars_read_current_line = 0; std::size_t lines_read = 0; };
```

## Instance state of `lexer` (members the function reads or writes)

```
int current;                  // the character read last: 0..255, or std::char_traits<char>::eof() (-1) at the end of the input
bool next_unget;              // true if the next get() must return `current` again (set by unget())
position_t position;          // position.chars_read_total = number of characters read so far (decreased by unget())
std::string token_string;     // characters of the current token, for error messages
const char* error_message;    // text describing the last error; set by the function before it returns token_type::parse_error
```

## Sibling member functions the function may call

```
std::char_traits<char>::int_type get();
    // reads the next character into `current` (taking a pending unget into account), increments position.chars_read_total, and returns it;
    // at the end of input `current` becomes std::char_traits<char>::eof() (-1)
void unget();   // makes the next get() return the same character again and decrements position.chars_read_total
bool skip_bom();
    // tries to skip a UTF-8 byte order mark at the current input position: reads one character; if it is 0xEF, the next two must be 0xBB, 0xBF
    // (returns true if so, false if not); if the first character is not 0xEF it is ungotten and true is returned
token_type scan_literal(const char* literal_text, const std::size_t length, token_type return_type);
    // `current` is the first character of literal_text; reads and compares the remaining length-1 characters; returns return_type on
    // success, or sets error_message = "invalid literal" and returns token_type::parse_error
token_type scan_string();    // `current` is the opening '"'; scans a whole string, returns token_type::value_string or token_type::parse_error (sets error_message)
token_type scan_number();    // `current` is '-' or a digit; scans a whole number, returns value_unsigned / value_integer / value_float or parse_error
```

=== STUB ===
```cpp
token_type scan()
{
    // TODO: implement according to the specification
}
```
