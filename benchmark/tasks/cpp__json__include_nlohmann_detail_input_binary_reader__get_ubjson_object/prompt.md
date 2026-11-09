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

`get_ubjson_object()` decodes the body of a UBJSON object (Universal Binary JSON) and reports it to the SAX handler: `start_object`, for every member a `key` event followed by the events of its value, and `end_object`. The opening `{` has already been read (it is the current byte). The object may be written in the plain form (members until a closing `}`), with a member count (`#<count>`), or with a count and a common value type (`$<type>#<count>`, in which the values carry no type markers).

## 2. Functional requirements

1. Read the container header (optional `$type`, optional `#count`; see `get_ubjson_size_type` in the context) to obtain the count (absent = "unknown") and the type (absent = none). If reading the header fails, return `false`.
2. **Count given** (`#n`): call `sax->start_object(n)`; if it returns `false`, return `false`. Then, `n` times: read a key (a UBJSON string without the `S` marker, i.e. a length marker with length and bytes), call `sax->key(key)`, then read the member's value:
   - if a type was given in the header, the value is read as a value of that type without a leading marker (payload only);
   - otherwise one complete UBJSON value with its marker is read (no-op `N` bytes in front of the marker are skipped).
   If any step fails (decoding error, or `false` from the handler), return `false` immediately. With `n == 0` no members are read.
3. **No count**: announce an unknown element count to the handler with `start_object` (the count argument is the largest value of `std::size_t`); if the call returns `false`, return `false`. The first byte after the header is already the first byte of the first key's length marker (or `}` for an empty object). Repeat while that current byte is not `}`: read the key (the length marker is the current byte), call `sax->key(key)`, read one complete UBJSON value with its marker, then read the next byte skipping `N` no-op bytes (it is either `}` or the length marker of the next key). Stop at the `}`.
4. Finally return the result of `sax->end_object()`.
5. Errors are reported through `sax->parse_error(...)` and make the function return what that call returns (`false`; the default DOM handler throws). Nothing further is read and no further events are produced after a failure.

## 3. Input specification

- The reader's input is positioned right after `{` (so `chars_read` counts it). Keys are strings: their length is given by a marker `U` (uint8), `i` (int8), `I` (int16), `l` (int32) or `L` (int64) followed by the big-endian integer, and then that many bytes. Counts use the same integer markers. Negative counts and counts that are not backed by enough input are outside the contract unless the input is short (then an end-of-input error is reported).
- Value markers: `T`, `F`, `Z`, `U`, `i`, `I`, `l`, `L`, `d`, `D`, `C`, `S`, `[`, `{` (no-op `N` is skipped where noted).

## 4. Output specification

Return value: `true` if the whole object was decoded and every handler call returned `true`, otherwise `false`. The handler receives, in input order: `start_object(count or -1)`, then per member `key(k)` and the value's events (`null`, `boolean`, `number_integer`/`number_unsigned` (`U` gives unsigned, the signed markers give integer), `number_float` (`d` and `D`), `string` (`S` and `C`), nested `start_array`/`end_array` and `start_object`/`end_object`), then `end_object`.

Errors (parse_error exceptions, message `[json.exception.parse_error.<id>] parse error at byte <N>: syntax error while parsing UBJSON <context>: <detail>`, `<N>` = number of bytes read at the failure, 1-based, counting the failed read at the end of input):

- id 110 (`unexpected end of input`, context `value`, `number`, `string`, `type`, `size`...): the input ended inside the structure, e.g. `{` alone fails with `... UBJSON value: unexpected end of input` at byte 2; a count/type header reports context `type` / `value`.
- id 113 `expected length type specification (U, i, I, l, L); last byte: 0x<HH>` (context `string`): a key's length marker is not one of `U i I l L` (also when the input ends in a position where a key marker must follow after a value: that case reports 110 context `value`).
- id 112 `invalid byte: 0x<HH>` (context `value`; `<HH>` is the byte that was read last: the marker itself for an untyped value, the last byte read for a typed container) for an unknown value marker (including `N` as a typed-container type); id 112/113 for malformed headers (id 112, context `size`: `expected '#' after type information; last byte: 0x<HH>`; id 113, context `size`: `expected length type specification (U, i, I, l, L) after '#'; last byte: 0x<HH>`).

## 5. Edge cases and constraints

- `{ }` (`7B 7D`): `start_object(-1)`, `end_object()`. `{ i 01 'a' i 01 }` gives `start_object(-1)`, `key("a")`, `number_integer(1)`, `end_object()`.
- `{ # i 02 i 01 'a' i 01 i 01 'b' i 02` (count 2, no closing byte): `start_object(2)`, `key("a")`, `number_integer(1)`, `key("b")`, `number_integer(2)`, `end_object()`; no closing `}` is read for a counted object.
- `{ $ i # i 02 i 01 'a' 01 i 01 'b' 02`: typed, values are bare int8 payloads: same events as above.
- `{ # i 00` gives `start_object(0)`, `end_object()`. In a typed object whose type is `T`, `F` or `Z`, each value is produced without reading any byte.
- `N` bytes between the members of an unsized object (after a value, or in front of a value marker) are ignored.
- A key whose length marker is invalid (for example `{ A`) fails with 113.

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

=== STUB ===
```cpp
bool get_ubjson_object()
{
    // TODO: implement according to the specification
}
```
