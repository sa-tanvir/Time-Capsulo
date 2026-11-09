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
