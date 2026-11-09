You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `decode_helper(input, num_chunks, config, output) -> Result<usize, DecodeError>`

## 1. Component overview

Part of the `base64` crate (v0.11). `decode_helper` is the shared core of every decoder in `src/decode.rs`:
`decode_config_buf` (and therefore `decode` / `decode_config`) and `decode_config_slice` both call it.
It decodes base64 text in `input` into raw bytes written at the start of `output`, using the alphabet and
trailing-bit policy of `config`, and returns how many bytes were written, or a precise `DecodeError`.
All decode tests of the crate (RFC 4648 vectors, padding errors, invalid bytes, round trips) go through it.

## 2. Functional requirements

**Alphabet.** Each symbol of the configured character set (`config.char_set`) stands for a 6-bit value 0..63
(Standard: `A-Z a-z 0-9 + /`; UrlSafe: `A-Z a-z 0-9 - _`; Crypt: `. / 0-9 A-Z a-z`, in that order). Its
256-entry lookup table (`config.char_set.decode_table()`) maps every byte to its value, or to
`tables::INVALID_VALUE` (255) if the byte is not in the alphabet. `=` (0x3D) is never an alphabet symbol; it may
only appear as padding as described below. No whitespace or other bytes are skipped.

**Decoding.** The symbols are concatenated as a big-endian bit stream, 6 bits each; every complete group of
8 bits becomes one output byte, in order. With `k` alphabet symbols (padding not counted) the output has
`floor(k * 3 / 4)` bytes: 4 symbols -> 3 bytes, 3 -> 2, 2 -> 1. Padding is optional and may be partial:
`"Zg=="`, `"Zg="` and `"Zg"` all decode to `"f"`.

**Validation, in this order (the first failure is returned):**

1. **Length.** If `input.len() % 4 == 1`, return `Err(DecodeError::InvalidLength)` before looking at any byte
   (e.g. `"E"`, `"ABCDE"`, `"====="`).
2. **Bytes, scanned from the start.** Split the input into 8-byte groups; the *final group* is the last one,
   i.e. the last `input.len() - 8 * (ceil(len / 8) - 1)` bytes (all 8 if the length is a multiple of 8).
   - Before the final group, every byte must be an alphabet symbol. The first one that is not (including `=`)
     gives `Err(InvalidByte(offset, byte))`.
   - Inside the final group, at position `i` (0-based, relative to the group start, which is a multiple of
     8 in `input`):
     - a `=` at `i % 4` equal to 0 or 1 is an error: `InvalidByte(offset, b'=')`, where `offset` is the
       index of the **first** `=` seen in the final group if one was already seen, otherwise this one;
     - a `=` at `i % 4` equal to 2 or 3 is accepted as padding;
     - any non-`=` byte after a `=` was seen is an error reported as `InvalidByte(offset_of_first_padding, b'=')`;
     - any other byte that is not in the alphabet gives `InvalidByte(its_offset, byte)`.
   Offsets are always absolute indices into `input`.
3. **Trailing bits.** If the last symbol carries bits that do not fit in a whole output byte (2 or 4 leftover
   bits) and any of them is 1, and `config.decode_allow_trailing_bits` is `false`, return
   `Err(InvalidLastSymbol(offset_of_last_symbol, last_symbol))`. When it is `true`, those bits are ignored.

Examples (Standard alphabet, trailing bits not allowed unless stated):

| input | result |
|---|---|
| `""` | `Ok(0)` |
| `"Zm9vYmFy"` | `Ok(6)`, `foobar` |
| `"Zm9vYmE="`, `"Zm9vYmE"` | `Ok(5)`, `fooba` |
| `"YWx\0pY2U=="` | `InvalidByte(3, 0)` |
| `"YWxpY2U====="` | `InvalidByte(7, b'=')` |
| `"YWxpY2UABB===="` | `InvalidByte(10, b'=')` |
| `"YWxpY2UABB=B"` | `InvalidByte(10, b'=')` |
| `"EEE==="` | `InvalidByte(3, b'=')` |
| `"EE===="` | `InvalidByte(2, b'=')` |
| `"E="`, `"E=="`, `"E==="` | `InvalidByte(1, b'=')` |
| `"=="`, `"===="` | `InvalidByte(0, b'=')` |
| `"ABCD" + "==Y=Wx===pY=2U====="` | `InvalidByte(4, b'=')` |
| `"iYV="` | `InvalidLastSymbol(2, b'V')`; with trailing bits allowed `Ok(2)`, `[137, 133]` |
| `"AAAAiYX="` | `InvalidLastSymbol(6, b'X')`; allowed: `[0, 0, 0, 137, 133]` |
| `"/x=="` / `"AAAA/x=="` | `InvalidLastSymbol(1, b'x')` / `InvalidLastSymbol(5, b'x')`; `"/w=="` is `[255]` |

Every 4-symbol string `s1 s2 s3 '='` either decodes to the 2 bytes whose padded encoding it is, or fails with
`InvalidLastSymbol(2, s3)`; likewise `s1 s2 '=' '='` decodes to 1 byte or fails with `InvalidLastSymbol(1, s2)`.

## 3. Input specification

- `input: &[u8]`: the encoded text, any length and any byte values.
- `num_chunks: usize`: always `ceil(input.len() / 8)` (what `num_chunks(input)` returns), passed in by the
  caller so it is not recomputed.
- `config: Config`: alphabet (`char_set`), `pad` (irrelevant for decoding) and `decode_allow_trailing_bits`.
- `output: &mut [u8]`: destination. Callers guarantee it is at least as long as the decoded data. It may be
  exactly that long (e.g. 1 byte for `"Zg="`, `input.len()*3/4` rounded down for unpadded input), or much longer:
  `decode_config_buf` passes `num_chunks * 6` bytes; `decode_config_slice` passes a slice in the middle of a
  larger caller buffer.

## 4. Output specification

- `Ok(n)`: `output[..n]` holds the decoded bytes; `n = floor(k * 3 / 4)` as above.
- **No byte of `output` at index `>= n` may be modified** (the tests check that the bytes after the decoded data
  in a caller buffer are untouched, and that an exactly-sized slice works without panicking).
- `Err(DecodeError::...)` as described in section 2. The contents of `output` after an error are unspecified.

## 5. Edge cases and constraints

- Empty input returns `Ok(0)` and writes nothing.
- Lengths with `len % 4 == 1` are always `InvalidLength`, even if they contain invalid bytes.
- `=` outside the final 8-byte group is just an invalid byte (e.g. `"ABCD" * n + "YWxpY2U====="` reports index
  `4n + 7`), even when it looks like padding of an earlier quad.
- Large inputs (megabytes) must decode in linear time without allocation; the function is pure apart from
  writing to `output`, and it must not panic for any input when `output` is large enough.

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/decode.rs`

## Imports / includes available in this file

```
use crate::{tables, Config};
use crate::STANDARD;
use alloc::vec::Vec;
use std::error;
use core::fmt;
    use super::*;
    use crate::{
        encode::encode_config_buf,
        encode::encode_config_slice,
        tests::{assert_encode_sanity, random_config},
    };
    use rand::{
        distributions::{Distribution, Uniform},
        FromEntropy, Rng,
    };
```

## Other functions defined in the same file (signatures only; you may call them)

```
cause & self
decode input : & T
decode_chunk input : & [ u8 ] , index_at_start_of_input : usize , decode_table : & [ u8 ; 256 ] , output : & mut [ u8 ] ,
decode_chunk_precise input : & [ u8 ] , index_at_start_of_input : usize , decode_table : & [ u8 ; 256 ] , output : & mut [ u8 ] ,
decode_chunk_precise_writes_only_6_bytes
decode_chunk_writes_8_bytes
decode_config input : & T , config : Config ,
decode_config_buf input : & T , config : Config , buffer : & mut Vec < u8 > ,
decode_config_slice input : & T , config : Config , output : & mut [ u8 ] ,
decode_into_nonempty_vec_doesnt_clobber_existing_prefix
decode_into_slice_doesnt_clobber_existing_prefix_or_suffix
decode_into_slice_fits_in_precisely_sized_slice
description & self
detect_invalid_last_symbol_every_possible_three_symbols
detect_invalid_last_symbol_every_possible_two_symbols
detect_invalid_last_symbol_one_byte
detect_invalid_last_symbol_two_bytes
fmt & self , f : & mut fmt :: Formatter
num_chunks input : & [ u8 ]
write_u64 output : & mut [ u8 ] , value : u64
```

## Types and constants used by this function (from `src/lib.rs`, `src/tables.rs` and this file)

```
pub struct Config { char_set: CharacterSet, pad: bool, decode_allow_trailing_bits: bool }   // Copy
pub enum CharacterSet { Standard, UrlSafe, Crypt }                                          // Copy
impl CharacterSet { fn decode_table(self) -> &'static [u8; 256] }  // byte -> 6-bit value, or INVALID_VALUE
tables::INVALID_VALUE: u8 = 255

pub enum DecodeError {
    InvalidByte(usize, u8),        // offset in input, offending byte
    InvalidLength,
    InvalidLastSymbol(usize, u8),  // offset in input, offending symbol
}

// constants defined at the top of src/decode.rs
const INPUT_CHUNK_LEN: usize = 8;
const DECODED_CHUNK_LEN: usize = 6;
const DECODED_CHUNK_SUFFIX: usize = 2;
const CHUNKS_PER_FAST_LOOP_BLOCK: usize = 4;
const INPUT_BLOCK_LEN: usize = 32;    // CHUNKS_PER_FAST_LOOP_BLOCK * INPUT_CHUNK_LEN
const DECODED_BLOCK_LEN: usize = 26;  // CHUNKS_PER_FAST_LOOP_BLOCK * DECODED_CHUNK_LEN + DECODED_CHUNK_SUFFIX
```

## Helpers in this file you may call

- `decode_chunk(input, index_at_start_of_input, decode_table, output)`: decodes the first 8 bytes of `input`
  (all must be alphabet symbols, else `Err(InvalidByte(index_at_start_of_input + i, byte))` for the first bad
  one) into 6 bytes, and writes **8** bytes to `output[0..8]` (the last 2 are zero filler).
- `decode_chunk_precise(...)`: same, but writes only `output[0..6]`.
- `num_chunks(input) -> usize`: `ceil(input.len() / 8)`.

=== STUB ===
```rust
fn decode_helper(
    input: &[u8],
    num_chunks: usize,
    config: Config,
    output: &mut [u8],
) -> Result<usize, DecodeError> {
    // TODO: implement according to the specification
}
```
