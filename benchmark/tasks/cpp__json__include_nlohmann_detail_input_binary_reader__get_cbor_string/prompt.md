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

`get_cbor_string(result)` decodes one CBOR text string (major type 3, RFC 7049) from the reader's input and appends its bytes to `result`. When it is called, the initial byte of the string has already been read and is in `current`; the function reads the length information, if any, and the payload bytes that follow, and reports problems to the SAX handler as parse errors.

## 2. Functional requirements

Let `current` be the initial byte when the function starts.

1. If `current` is end-of-input (-1), an error is reported (see section 4, error A) and its result returned.
2. Definite-length strings. The initial byte selects the length:
   - `0x60`..`0x77`: the length is the low five bits of the initial byte (0 to 23); that many payload bytes follow immediately.
   - `0x78`: one length byte follows (unsigned 8-bit); `0x79`: two bytes (unsigned 16-bit, big-endian); `0x7A`: four bytes (32-bit, big-endian); `0x7B`: eight bytes (64-bit, big-endian). The payload of that many bytes follows.
   All payload bytes are appended to `result` unchanged, in order, with no UTF-8 validation.
3. Indefinite-length string, initial byte `0x7F`. A sequence of chunks follows, each of which is itself a complete text string item (definite or again indefinite, so chunks may nest), terminated by the break byte `0xFF`. The contents of all chunks are appended to `result` in order. The break byte is consumed.
4. Any other initial byte (including the byte string, array, map, tag and simple-value initial bytes, and `0xFF` as a chunk header) is an error (see section 4, error C).
5. On success the function returns `true` and has consumed exactly the bytes of the string item (initial byte, length bytes, payload; for indefinite strings every chunk and the break byte); no byte after the item is read.
6. Errors are reported by calling `sax->parse_error(chars_read, last_token, exception)` and returning the value it returns (`false` for a handler that does not throw; the default handler throws the exception). Parsing stops at the first error. The function returns `false` otherwise only in this way.

## 3. Input specification

- `result`: a string, empty when the function is called; payload bytes are appended.
- Input: the reader's byte stream positioned right after the initial byte. Lengths larger than the remaining input are only meaningful when the stream is short (an error is reported at the first missing byte); huge lengths with a long input are out of contract.

## 4. Output specification

Return value: `true` when a whole string was read, otherwise the result of the `parse_error` call (normally `false`). `result` holds the decoded text on success; on failure its content is unspecified. `chars_read` is the number of bytes consumed so far (the byte numbering used in the messages below is 1-based: byte 1 is the first byte of the whole input).

Errors, all `parse_error` exceptions whose `what()` is `[json.exception.parse_error.<id>] parse error at byte <N>: syntax error while parsing CBOR <context>: <detail>` where `<N>` is the value of `chars_read` at the moment of the failure (the 1-based number of the offending or missing byte):

- **A, id 110**, context `string` or `number`, detail `unexpected end of input`: the input ended where the initial byte was expected (context `string`), inside a length field (context `number`) or inside the payload (context `string`); also when an indefinite string ends without a break byte (the chunk header is then missing: context `string`). `<N>` counts the failed read, e.g. the input `78` fails at byte 2 and `61` (one payload byte missing) at byte 2.
- **C, id 113**, context `string`, detail `expected length specification (0x60-0x7B) or indefinite string type (0x7F); last byte: 0x<HH>` where `<HH>` is the offending byte in two uppercase hexadecimal digits (for example `0x41`, `0xFF`). `<N>` is the position of that byte. The last-token argument of `parse_error` is `<HH>`.

## 5. Edge cases and constraints

- `60` gives the empty string; `7F FF` gives the empty string; `62 61 62` gives `"ab"`; `78 18` followed by 24 bytes gives those 24 bytes; `7F 61 61 62 62 62 FF` gives `"abb"`; `7F 7F 61 61 FF 62 62 62 FF` gives `"abb"` (a chunk that is itself indefinite).
- A string may contain any bytes (also `0x00` and bytes >= `0x80`) in its payload.
- Non-minimal length encodings are accepted (`78 01 61` is the string `"a"`).
- Error examples: input `41` (byte string) fails with 113 at byte 1, last byte `0x41`; `7F 41` fails at byte 2; `7F 61 61` (no break) fails with 110 at byte 4; empty input fails with 110 at byte 1 (context `string`).

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

There is no template line above the stub. The caller (`parse_cbor_internal`) reads the string's initial byte with `get()` first and then calls the function; the same function is used to read map keys.

=== STUB ===
```cpp
bool get_cbor_string(string_t& result)
{
    // TODO: implement according to the specification
}
```
