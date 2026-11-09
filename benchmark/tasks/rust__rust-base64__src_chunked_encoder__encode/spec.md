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
