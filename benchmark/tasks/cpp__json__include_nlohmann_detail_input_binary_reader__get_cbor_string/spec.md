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
