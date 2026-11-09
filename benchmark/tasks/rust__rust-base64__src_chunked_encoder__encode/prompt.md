You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `ChunkedEncoder::encode(&self, bytes, sink) -> Result<(), S::Error>`

## 1. Component overview

Part of the `base64` crate (v0.11). A `ChunkedEncoder` base64-encodes a byte slice **without heap allocation**
and hands the encoded text to a `Sink` piece by piece. It is the engine behind `encode_config_buf` (sink that
appends to a `String`) and `display::Base64Display` (sink that writes to a `fmt::Formatter`, so
`format!("{}", Base64Display::with_config(data, cfg))` works). `encode` performs one complete encoding of
`bytes` with the encoder's configuration.

## 2. Functional requirements

1. Encode `bytes` as base64 using the alphabet of `self.config` (`self.config.char_set`; its 64-symbol table is
   available as `self.config.char_set.encode_table()`):
   every 3 input bytes become 4 symbols (big-endian 6-bit groups); a final group of 1 byte becomes 2 symbols and
   of 2 bytes becomes 3 symbols (the unused low bits are zero).
2. If `self.config.pad` is `true`, a final 1-byte group is followed by `==` and a final 2-byte group by `=`, so
   the total length is a multiple of 4. Without padding nothing is appended.
3. Deliver the encoded text by calling `sink.write_encoded_bytes(chunk)` one or more times, in order. The
   concatenation of all chunks must be **byte-for-byte identical** to `encode_config(bytes, self.config)`;
   padding appears only at the very end.
4. No heap allocation: use a fixed stack buffer of 1024 (`BUF_SIZE`) bytes; each chunk passed to the sink is at
   most 1024 bytes. Each chunk should encode a whole number of 3-byte groups, except the last one; the encoder's
   precomputed `self.max_input_chunk_len` is the number of input bytes that fit in one chunk while leaving room
   for padding (765 when padding, 768 otherwise).
5. If the sink returns `Err(e)`, stop immediately and return `Err(e)`; otherwise return `Ok(())` after all
   input has been delivered.

Examples (Standard alphabet, padding on unless stated; output = concatenation of chunks):

| `bytes` | output |
|---|---|
| `b""` | `""` (the sink is not called) |
| `b"foobar"` | `"Zm9vYmFy"` |
| `b"foobarf"` | `"Zm9vYmFyZg=="` |
| `b"foobarbazqux"` | `"Zm9vYmFyYmF6cXV4"` |
| `b"foobarbazquxquuxcorgegraultgarplyz"` | `"Zm9vYmFyYmF6cXV4cXV1eGNvcmdlZ3JhdWx0Z2FycGx5eg=="` |
| `b"foobarf"`, `STANDARD_NO_PAD` | `"Zm9vYmFyZg"` |
| `[0x0, 0x1, 0x2, 0x3]` | `"AAECAw=="` |

For random inputs of 1..10 000 bytes and any of the three alphabets with or without padding, the result must
equal `encode_config_buf`'s normal encoding (this is what the tests check, through both the `String` sink and
`Base64Display`).

## 3. Input specification

- `&self`: a `ChunkedEncoder` built by `ChunkedEncoder::new(config)` (see the instance state in the context).
- `bytes: &[u8]`: arbitrary data, 0 to many megabytes.
- `sink: &mut S` where `S: Sink`; `write_encoded_bytes(&mut self, &[u8]) -> Result<(), S::Error>` receives
  ASCII (valid UTF-8) bytes. Sinks may append to existing content; `encode` must only call the sink, never
  assume or clear its previous contents.

## 4. Output specification

- Returns `Ok(())` on success, or the first error returned by the sink.
- The only effect is the sequence of sink calls; `self` and `bytes` are not modified.

## 5. Edge cases and constraints

- Empty input: no sink call, `Ok(())`.
- Inputs longer than one chunk must be split so that no padding or partial group appears in the middle, and the
  1024-byte buffer is never overrun (a padded final chunk of 765 input bytes plus padding must fit).
- Linear time; the sink may be called O(len / 768) times.

=== CONTEXT ===
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

=== STUB ===
```rust
pub fn encode<S: Sink>(&self, bytes: &[u8], sink: &mut S) -> Result<(), S::Error> {
    // TODO: implement according to the specification
}
```
