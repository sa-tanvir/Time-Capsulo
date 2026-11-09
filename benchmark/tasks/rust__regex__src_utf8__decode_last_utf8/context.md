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
