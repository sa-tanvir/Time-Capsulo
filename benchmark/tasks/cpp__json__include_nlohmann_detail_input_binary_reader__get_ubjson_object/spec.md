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
