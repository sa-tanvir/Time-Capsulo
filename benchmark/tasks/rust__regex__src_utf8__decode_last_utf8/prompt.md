You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `decode_last_utf8(src: &[u8]) -> Option<(char, usize)>`

## 1. Component overview

Part of the `regex` crate's small UTF-8 toolkit, used by the matching engines when they need the character
that **precedes** a position in a byte haystack (e.g. for word boundaries `\b`, multi-line anchors and
reverse searches on `&[u8]` input that may contain invalid UTF-8). It is the mirror image of
`decode_utf8` (see `context.md`): it decodes the **last** UTF-8 encoded character of `src`.

## 2. Functional requirements

1. If `src` is empty, return `None`.
2. Locate the start of the final sequence: let `k` be the index of the **last** byte of `src` that is not a
   continuation byte (a continuation byte has the bit pattern `10xxxxxx`), looking only at the final 4
   bytes of `src` (indices `>= src.len().saturating_sub(4)`). If all of those bytes are continuation
   bytes, return `None`.
3. Return `Some((c, src.len() - k))` if the bytes `src[k..]` are **exactly one** complete, valid UTF-8
   encoding of the character `c`; otherwise return `None`. Valid means: a correct lead byte, the right
   number of continuation bytes, the shortest possible encoding (no overlong forms), not a surrogate
   (U+D800–U+DFFF), and not above U+10FFFF. "Exactly one" means a valid sequence followed by extra
   bytes (e.g. `[0xC3, 0xA9, 0xA9]` or `b"a\x80"`) gives `None`, as does a truncated one.
4. In particular, if the last byte is ASCII (`<= 0x7F`) the result is `Some((that byte as char, 1))`
   regardless of what precedes it.
5. The returned length is always 1, 2, 3 or 4, and always equals `c.len_utf8()`.
6. Bytes before the final sequence are never inspected beyond the 4-byte window and do not affect the
   result (so `b"x\xC3\xA9"` gives `Some(('é', 2))` and `b"\xFF\xFF" ++ "日"` gives `Some(('日', 3))`).

Examples:

| `src` | result |
|---|---|
| `[]` | `None` |
| `b"a"` | `Some(('a', 1))` |
| `[0xC3, 0xA9]` | `Some(('é', 2))` |
| `[0xE6, 0x97, 0xA5]` | `Some(('日', 3))` |
| `[0xF0, 0x9F, 0x98, 0x80]` | `Some(('😀', 4))` |
| `[0xFF]` | `None` (invalid start byte) |
| `[0xED, 0xA0, 0x81]` | `None` (surrogate) |
| `[0xC3]`, `[0xEF, 0xBF]`, `[0xF4, 0x8F, 0xBF]` | `None` (truncated) |
| `[0xC0, 0xA1]`, `[0xE0, 0x80, 0xA1]`, `[0xF0, 0x80, 0x80, 0xA1]` | `None` (not shortest form) |
| `[0xF4, 0x90, 0x80, 0x80]` | `None` (above U+10FFFF) |
| `[0x80]`, `[0x80, 0x80, 0x80, 0x80, 0x80]` | `None` (only continuation bytes) |
| `b"ab\xF0\x9F\x98"` | `None` (truncated 4-byte sequence) |

Property: for every `char` `c`, `decode_last_utf8(c.encode_utf8(..).as_bytes()) == Some((c, c.len_utf8()))`,
and for any valid UTF-8 string `s`, the decoded char equals `s.chars().rev().next()`.

## 3. Input specification

- `src: &[u8]`: arbitrary bytes of any length (often a prefix `&haystack[..i]` of a larger buffer); may be
  invalid UTF-8 anywhere.

## 4. Output specification

- `Option<(char, usize)>`: the last character and the number of bytes it occupies at the end of `src`, or
  `None` if the end of `src` is not a single valid UTF-8 sequence as described.

## 5. Edge cases and constraints

- Must never panic or read out of bounds for any input, including inputs shorter than 4 bytes.
- Pure function, no allocation, no mutation; constant work per call (independent of `src.len()`).
- Called once per position when walking a haystack backwards, so it should be cheap.

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/utf8.rs`

## Imports / includes available in this file

```
use std::char;
    use std::str;
    use quickcheck::quickcheck;
    use super::{
        TAG_CONT, TAG_TWO, TAG_THREE, TAG_FOUR,
        decode_utf8, decode_last_utf8,
    };
```

## Other functions defined in the same file (signatures only; you may call them)

```
(char)->
decode_utf8 src : & [ u8 ]
is_start_byte b : u8
next_utf8 text : & [ u8 ] , i : usize
p cp : char
p given_cp : char
reject_invalid
reject_invalid_last
```

## Constants and sibling functions in this file

- `TAG_CONT = 0b1000_0000`, `TAG_TWO = 0b1100_0000`, `TAG_THREE = 0b1110_0000`, `TAG_FOUR = 0b1111_0000` (`u8`).
- `decode_utf8(src: &[u8]) -> Option<(char, usize)>`: decodes the **first** UTF-8 sequence of `src`; returns the
  character and its length (1-4) or `None` if `src` is empty or does not start with a valid, shortest-form,
  non-surrogate, `<= U+10FFFF` sequence. Bytes after that sequence are ignored.
- `is_start_byte(b: u8) -> bool`: true iff `b` is not a continuation byte (i.e. `b & 0b1100_0000 != 0b1000_0000`).

=== STUB ===
```rust
pub fn decode_last_utf8(src: &[u8]) -> Option<(char, usize)> {
    // TODO: implement according to the specification
}
```
