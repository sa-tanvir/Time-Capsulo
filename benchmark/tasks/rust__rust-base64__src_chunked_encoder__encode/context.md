# Context for the function to implement

- **Language:** rust
- **File:** `src/chunked_encoder.rs`
- **Enclosing scope:** `impl ChunkedEncoder`

## Imports / includes available in this file

```
use crate::{
    encode::{add_padding, encode_to_slice},
    Config,
};
use alloc::string::String;
use core::cmp;
use core::str;
    use super::*;
    use crate::{encode_config_buf, tests::random_config, CharacterSet, STANDARD};
    use rand::{
        distributions::{Distribution, Uniform},
        FromEntropy, Rng,
    };
```

## Other functions defined in the same file (signatures only; you may call them)

```
chunked_encode_empty
chunked_encode_fast_loop
chunked_encode_intermediate_fast_loop
chunked_encode_matches_normal_encode_random sink_test_helper : & S
chunked_encode_matches_normal_encode_random_string_sink
chunked_encode_slow_loop_only
chunked_encode_str bytes : & [ u8 ] , config : Config
config_with_pad pad : bool
encode_to_string & self , config : Config , bytes : & [ u8 ]
max_input_length encoded_buf_len : usize , config : Config
max_input_length_cant_use_extra_single_encoded_byte
max_input_length_no_pad
max_input_length_with_pad_decrements_one_triple
max_input_length_with_pad_fits_exactly
max_input_length_with_pad_one_byte_short
new config : Config
new s : & mut String
write_encoded_bytes & mut self , encoded : & [ u8 ]
write_encoded_bytes & mut self , s : & [ u8 ]
```

## Instance state (`struct ChunkedEncoder`)

```
pub struct ChunkedEncoder {
    config: Config,               // alphabet + padding flag (Copy)
    max_input_chunk_len: usize,   // = max_input_length(BUF_SIZE, config): 765 if config.pad, else 768
}
const BUF_SIZE: usize = 1024;     // module constant

pub trait Sink {
    type Error;
    fn write_encoded_bytes(&mut self, encoded: &[u8]) -> Result<(), Self::Error>;
}
```

## Related items

```
pub struct Config { char_set: CharacterSet, pad: bool, decode_allow_trailing_bits: bool }   // Copy
impl CharacterSet { fn encode_table(self) -> &'static [u8; 64] }

// from crate::encode (imported above)
// Encodes `input` without padding into the start of `output` (which must be large enough);
// returns the number of bytes written.
pub fn encode_to_slice(input: &[u8], output: &mut [u8], encode_table: &[u8; 64]) -> usize
// Writes (3 - input_len % 3) % 3 bytes of b'=' to the start of `output`; returns how many were written.
pub fn add_padding(input_len: usize, output: &mut [u8]) -> usize
```
