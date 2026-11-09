# Functional specification

## 1. Component overview

`get_ubjson_array()` decodes the body of a UBJSON array (Universal Binary JSON) and reports it to the SAX handler: `start_array`, the events of every element, and `end_array`. The opening `[` has already been read (it is the current byte). The array may be written in the plain form (elements until a closing `]`), with an element count (`#<count>`), or with a count and a common element type (`$<type>#<count>`, in which the elements carry no type markers).

## 2. Functional requirements

1. Read the container header (optional `$type`, optional `#count`; see `get_ubjson_size_type` in the context) to obtain the count (absent = "unknown") and the type (absent = none). If reading the header fails, return `false`.
2. **Count given** (`#n`): call `sax->start_array(n)`; if it returns `false`, return `false`. Then:
   - if a type was given and it is the no-op type `N`, no elements are read (no element events at all);
   - if another type was given, `n` elements are read, each as a value of that type without a leading marker (payload only);
   - if no type was given, `n` complete UBJSON values with their markers are read (no-op `N` bytes in front of a marker are skipped).
   If any element fails (decoding error or `false` from the handler), return `false` immediately. With `n == 0` nothing is read.
3. **No count**: announce an unknown element count to the handler with `start_array` (the count argument is the largest value of `std::size_t`); if the call returns `false`, return `false`. The current byte after the header is already the first byte of the first element (its type marker), or `]` for an empty array. Repeat while the current byte is not `]`: read one complete UBJSON value whose marker is the current byte, then read the next byte skipping `N` no-op bytes (it is either `]` or the marker of the next element). Stop at the `]`.
4. Finally return the result of `sax->end_array()`.
5. Errors are reported through `sax->parse_error(...)` and make the function return what that call returns (`false`; the default DOM handler throws). Nothing further is read and no further events are produced after a failure.

## 3. Input specification

- The reader's input is positioned right after `[` (so `chars_read` counts it). Counts are given by an integer marker `U` (uint8), `i` (int8), `I` (int16), `l` (int32) or `L` (int64) followed by the big-endian integer. Negative counts and counts that are not backed by enough input are outside the contract unless the input is short (then an end-of-input error is reported); also avoid very large counts for the payload-less types `T`, `F`, `Z`.
- Element markers: `T`, `F`, `Z`, `U`, `i`, `I`, `l`, `L`, `d`, `D`, `C`, `S`, `[`, `{`. In a typed array the type is one of these (elements of type `[` or `{` omit the opening bracket; their content follows directly).

## 4. Output specification

Return value: `true` if the whole array was decoded and every handler call returned `true`, otherwise `false`. The handler receives, in input order: `start_array(count or -1)`, then for each element its events (`null`, `boolean`, `number_integer`/`number_unsigned` (`U` gives unsigned, the signed markers give integer), `number_float` (`d` and `D`), `string` (`S` and `C`), nested `start_array`/`end_array` and `start_object`/`end_object`), then `end_array`.

Errors (parse_error exceptions, message `[json.exception.parse_error.<id>] parse error at byte <N>: syntax error while parsing UBJSON <context>: <detail>`, `<N>` = number of bytes read at the failure, 1-based, counting the failed read at the end of input):

- id 110 (`unexpected end of input`, context `value`, `number`, `string`, `type`, `size`, `char`): the input ended inside the structure; for example `[` alone fails with `... UBJSON value: unexpected end of input` at byte 2.
- id 112 `invalid byte: 0x<HH>` (context `value`; `<HH>` is the byte that was read last: the marker itself for an untyped value, the last byte read for a typed container) for an unknown element marker (including `N` as the type of a typed array when the elements are read; `A`, `}` etc. are unknown); malformed headers give id 112 (context `size`: `expected '#' after type information; last byte: 0x<HH>`) or 113 (context `size`: `expected length type specification (U, i, I, l, L) after '#'; last byte: 0x<HH>`).
- id 113 for a `C` element whose byte is above 0x7F (`byte after 'C' must be in range 0x00..0x7F; last byte: 0x<HH>`, context `char`).

## 5. Edge cases and constraints

- `[ ]` (`5B 5D`): `start_array(-1)`, `end_array()`. `[ i 01 i 02 ]`: `start_array(-1)`, `number_integer(1)`, `number_integer(2)`, `end_array()`.
- `[ # i 02 i 01 i 02` (count 2, no closing byte): `start_array(2)`, two `number_integer` events, `end_array()`; no closing `]` is read for a counted array.
- `[ $ i # i 03 01 02 03`: typed array of bare int8 payloads: `start_array(3)`, `number_integer(1)`, `(2)`, `(3)`, `end_array()`. `[ $ T # i 03`: three `boolean(true)` events without reading any byte. `[ $ N # i 03`: only `start_array(3)` and `end_array()`.
- `[ # i 00` gives `start_array(0)`, `end_array()`.
- `N` bytes between the elements of an unsized array (after an element, or in front of an element marker) are ignored.
- Elements may be arrays or objects (`[ [ i 01 ] { i 01 'a' Z } ]`).
