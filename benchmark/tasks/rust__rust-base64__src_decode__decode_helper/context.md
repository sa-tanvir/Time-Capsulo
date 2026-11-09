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
