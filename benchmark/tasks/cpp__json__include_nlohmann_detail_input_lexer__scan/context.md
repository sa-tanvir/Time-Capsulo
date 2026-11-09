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
