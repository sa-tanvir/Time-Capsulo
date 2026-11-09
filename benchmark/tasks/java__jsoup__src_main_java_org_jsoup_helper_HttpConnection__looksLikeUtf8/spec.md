# Functional specification

## 1. Component overview

`looksLikeUtf8(input)` is a heuristic check used when decoding HTTP header values: it decides whether a byte array is plausibly UTF-8 encoded text. It is a structural check (lead and continuation bytes), not a full validator.

## 2. Functional requirements

Treat each byte as unsigned (0..255).

1. If the array starts with the three bytes `EF BB BF` (UTF-8 byte order mark), skip them and examine the rest.
2. Scan the remaining bytes from left to right:
   - A byte below `0x80` (high bit clear) is ASCII and acceptable on its own.
   - A byte of the form `110xxxxx` starts a 2-byte sequence (one continuation byte follows); `1110xxxx` starts a 3-byte sequence (two continuation bytes); `11110xxx` starts a 4-byte sequence (three continuation bytes).
   - Any other byte with the high bit set in a leading position (a stray continuation byte `10xxxxxx`, or `11111xxx` such as `0xF8..0xFF`) makes the result `false`.
   - For a sequence with `k` continuation bytes starting at index `i`, the array must have those `k` bytes after position `i`, and the last of them must not be the final byte of the array: if the index of the last continuation byte (`i + k`) is `>=` the array length, the result is `false`. Note that this means a multi-byte sequence ending exactly at the end of the array is accepted, but one that would run past the end is rejected.
   - Every continuation byte must have the form `10xxxxxx`, otherwise `false`.
   - After a complete sequence, scanning resumes at the byte after it.
3. If the whole array is scanned without failure, return `true`. An empty array, a BOM alone, and pure ASCII all return `true`.

The check does not reject overlong encodings, surrogate code points or values above U+10FFFF as long as lead/continuation structure is right.

## 3. Input specification

`input`: a non-null `byte[]` of any length from 0 up to several hundred thousand bytes.

## 4. Output specification

A `boolean`. Examples: `{}` true; `{0x41}` true; `{0xC3, 0xA9}` true; `{0xC3}` false; `{0xC3, 0x28}` false; `{0xE2, 0x82, 0xAC}` true; `{0xE2, 0x82}` false; `{0xF0, 0x9F, 0x98, 0x80}` true; `{0xFF}` false; `{0x80}` false; `{0xEF, 0xBB, 0xBF, 0x41}` true; `{0xEF, 0xBB}` false (the first byte `0xEF` begins a 3-byte sequence that is cut off); `{0xEF, 0xBB, 0xBF, 0xC3}` false; `{0x63, 0x61, 0x66, 0xE9}` false (a Latin-1 string).

## 5. Edge cases and constraints

- The array is not modified. The method has no side effects and is a pure function of its argument.
- Must make a single pass; it is applied to large arrays.
