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

`get_cbor_object(len)` decodes the members of a CBOR map (major type 5, RFC 7049) from the reader's input and reports them to the SAX handler as events: `start_object`, then for every member a `key` event followed by the events of its value, then `end_object`. The map's initial byte (and its length bytes) have already been consumed; `len` is the declared number of members, or `std::size_t(-1)` when the map has indefinite length.

## 2. Functional requirements

1. First `sax->start_object(len)` is called with `len` unchanged (`std::size_t(-1)` for an indefinite map). If it returns `false`, the function returns `false` immediately without reading any input.
2. **Definite map** (`len != std::size_t(-1)`): the following is done `len` times, in order. The next input byte is read; it is the initial byte of the member's key, which must be a CBOR text string (definite or indefinite, decoded exactly as by `get_cbor_string`). Then `sax->key(key)` is called with the decoded key. Then one complete CBOR value (any type, arbitrarily nested, decoded as by `parse_cbor_internal()`) is read and reported to the handler. A map with `len == 0` reads nothing more.
3. **Indefinite map**: repeat: read the next byte; if it is the break byte `0xFF` the map ends; otherwise that byte is the initial byte of a key and the member is processed exactly as in rule 2 (key, `sax->key`, value).
4. After the last member (or the break byte), the function returns the result of `sax->end_object()`.
5. If any step fails the function returns `false` at once (nothing further is read and no further events are produced): the failing steps are a SAX call that returns `false` (`start_object`, `key`, or an event of a value, or `end_object`) and a decoding error. A decoding error is reported through `sax->parse_error(...)` (the default handler throws), and the function returns what the failed step returned.
6. The member keys must be text strings. A key whose initial byte is not a text string initial byte (`0x60`..`0x7B`, `0x7F`) is an error 113 as described below; the end of the input in a key or value is an error 110.

## 3. Input specification

- `len`: the declared member count; `std::size_t(-1)` means indefinite length. When the count is definite and larger than the number of members actually present, the missing members produce an end-of-input error (110) at the first missing byte.
- The input stream is positioned directly after the map's initial byte (and length bytes), so `chars_read` already counts them.

## 4. Output specification

Return value: `true` if the whole map was decoded and every handler call returned `true`; otherwise `false`. Events are delivered to the handler in input order. Value events are the usual ones: unsigned/negative integers and floats as `number_unsigned` / `number_integer` / `number_float`, booleans, null, strings, and nested maps/arrays as `start_object`/`end_object`, `start_array`/`end_array` (with `std::size_t(-1)` as the count for indefinite-length containers).

Errors (parse_error exceptions; `<N>` is the 1-based number of the offending or missing input byte, i.e. `chars_read` at the failure):

- id 113, key is not a string: `[json.exception.parse_error.113] parse error at byte <N>: syntax error while parsing CBOR string: expected length specification (0x60-0x7B) or indefinite string type (0x7F); last byte: 0x<HH>` (`HH` = offending byte, two uppercase hex digits).
- id 110, input ended: `[json.exception.parse_error.110] parse error at byte <N>: syntax error while parsing CBOR <string|number|value>: unexpected end of input`.
- Errors inside values (for example id 112 `syntax error while parsing CBOR value: invalid byte: 0x<HH>`) are those of the value decoder and are passed on.

## 5. Edge cases and constraints

- `A0` with `len == 0`: events `start_object(0)`, `end_object()`; `BF FF` with `len == -1`: `start_object(-1)`, `end_object()`.
- `A1 61 61 01` (`{"a": 1}`): `start_object(1)`, `key("a")`, `number_unsigned(1)`, `end_object()`.
- `A1 61 61 A1 61 62 F5`: nested map `{"a": {"b": true}}`.
- `A1 01 02` fails with 113 at byte 2 (`last byte: 0x01`): the key is an integer. `A2 61 61 01` (declares two members but ends after one) fails with 110 at byte 5 (context `string`).
- Refusal: if the handler's `key` call returns `false` for the first key, the function returns `false` and the value is not read.
- The final break byte of an indefinite map is consumed; nothing after the map is read.

=== CONTEXT ===
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

## CBOR sibling functions

```
bool parse_cbor_internal(const bool get_char = true);
    // parses ONE complete CBOR data item (any type) and reports it to the SAX handler as events; with get_char == true it first reads the item's
    // initial byte with get(). Returns false if the handler refused an event or an error was reported.
bool get_cbor_string(string_t& result);
    // parses a CBOR text string whose initial byte is already in `current` (see the other task of this class); appends the text to result
```

## Declaration

There is no template line above the stub. The caller (`parse_cbor_internal`) has already consumed the map's initial byte and its length bytes, determined the member count `len` (or `std::size_t(-1)` for an indefinite-length map, initial byte `0xBF`), and then calls the function.

=== STUB ===
```cpp
bool get_cbor_object(const std::size_t len)
{
    // TODO: implement according to the specification
}
```
