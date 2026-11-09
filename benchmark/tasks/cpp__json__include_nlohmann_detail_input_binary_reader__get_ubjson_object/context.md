# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/nlohmann/detail/input/binary_reader.hpp` (nlohmann/json 3.7.2), inside
  `template<typename BasicJsonType, typename SAX = json_sax_dom_parser<BasicJsonType>> class binary_reader { ... }` in `namespace nlohmann::detail`.
  Headers available: `<array>`, `<cstdint>`, `<string>`, `<utility>`, `nlohmann/detail/exceptions.hpp`, `nlohmann/detail/input/input_adapters.hpp`, `nlohmann/detail/macro_scope.hpp` (`JSON_HEDLEY_UNLIKELY`, ...).
- The stub is a **private non-static member function** of `binary_reader`; unqualified names below resolve inside the class. `not`, `and`, `or` are the alternative tokens for `!`, `&&`, `||`.

## Instance state of `binary_reader`

```
using string_t = typename BasicJsonType::string_t;     // std::string
input_adapter_t ia;        // the byte source (not used directly by the function)
int current;               // the byte read last: 0..255, or std::char_traits<char>::eof() (-1) once the input is exhausted
std::size_t chars_read;    // number of read() calls so far: bytes consumed, counting a failed read at the end of input too
SAX* sax;                  // the SAX handler that receives the parse events (see below)
```

`SAX` provides (every event function returns `bool`; `false` means "stop parsing"):

```
bool null();                                    bool boolean(bool val);
bool number_integer(number_integer_t val);      bool number_unsigned(number_unsigned_t val);
bool number_float(number_float_t val, const string_t& s);
bool string(string_t& val);
bool start_object(std::size_t elements);        // elements == std::size_t(-1) when the number of members is unknown
bool key(string_t& val);                        bool end_object();
bool start_array(std::size_t elements);         bool end_array();
bool parse_error(std::size_t position, const std::string& last_token, const detail::exception& ex);
    // reports an error; returns false (the default DOM handler throws `ex` instead of returning)
```

## Helper members of `binary_reader` that the function may call

```
int get();
    // reads the next byte of the input into `current` (which is also returned) and increments `chars_read`;
    // at the end of the input `current` becomes std::char_traits<char>::eof() (-1) and chars_read is still incremented
template<typename NumberType, bool InputIsLittleEndian = false>
bool get_number(const input_format_t format, NumberType& result);
    // reads sizeof(NumberType) bytes (network byte order) into result; returns false after reporting a parse error 110 ("number") if the input ends
template<typename NumberType>
bool get_string(const input_format_t format, const NumberType len, string_t& result);
    // appends the next `len` bytes of the input to result; returns false after reporting error 110 ("string") if the input ends first
bool unexpect_eof(const input_format_t format, const char* context) const;
    // returns true unless `current` is EOF; otherwise reports parse_error 110 ("unexpected end of input", given context) through sax->parse_error and returns its result
std::string get_token_string() const;
    // `current` as two uppercase hexadecimal digits, e.g. "41"
std::string exception_message(const input_format_t format, const std::string& detail, const std::string& context) const;
    // "syntax error while parsing <CBOR|MessagePack|UBJSON|BSON> <context>: <detail>"
enum class input_format_t { json, cbor, msgpack, ubjson, bson };
```

`detail::parse_error::create(int id, std::size_t byte, const std::string& what_arg)` builds the exception whose `what()` is
`[json.exception.parse_error.<id>] parse error at byte <byte>: <what_arg>`.
A typical error report is: `return sax->parse_error(chars_read, token_text, parse_error::create(113, chars_read, exception_message(format, "...", "context")));`

## UBJSON sibling functions

```
int get_ignore_noop();
    // like get(), but skips every 'N' (no-op) byte: reads bytes until one is not 'N'; the result is also in `current`
bool parse_ubjson_internal(const bool get_char = true);
    // parses ONE complete UBJSON value with its type marker and reports it to the SAX handler; with get_char == true it first reads the
    // marker with get_ignore_noop(), otherwise the marker is the byte already in `current`. Returns false if refused or an error was reported.
bool get_ubjson_value(const int prefix);
    // parses the payload of a value whose type marker `prefix` is already known (the marker byte itself is not read again):
    // 'T', 'F', 'Z' have no payload; 'U','i','I','l','L' are followed by a big-endian integer; 'd','D' by a float/double; 'C' by one byte; 'S' by a
    // UBJSON string; '[' and '{' by the rest of the container. Reports the value to the SAX handler; unknown prefixes (including 'N') and EOF are errors.
bool get_ubjson_string(string_t& result, const bool get_char = true);
    // reads a length-prefixed string: a length marker (U, i, I, l, L) with its integer, then that many bytes. With get_char == true the marker is
    // read with get() first, otherwise `current` is the marker. Appends to result.
bool get_ubjson_size_type(std::pair<std::size_t, int>& result);
    // reads the optional container header that follows '[' or '{': an optional "$<type>" and an optional "#<count>" (a '$' type must be followed
    // by '#'). Skips 'N' bytes in front of the header. result.first = the count, or string_t::npos (== std::size_t(-1)) when no count is given;
    // result.second = the type marker byte, or 0 when no type is given. On return `current` is the last byte read: when no count is present it is
    // the first byte after the (empty) header. Returns false after reporting an error.
```

## Declaration

There is no template line above the stub. The caller has already read the `{` marker (it is in `current`) and then calls the function.
