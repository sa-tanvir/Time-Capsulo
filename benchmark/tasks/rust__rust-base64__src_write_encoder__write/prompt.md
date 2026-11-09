You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `<EncoderWriter as std::io::Write>::write(&mut self, input) -> io::Result<usize>`

## 1. Component overview

Part of the `base64` crate (v0.11), module `write`. `EncoderWriter<'a, W>` is a streaming encoder: it implements
`std::io::Write`, base64-encodes the bytes written to it and forwards the encoded text to a wrapped writer
`self.w` (the *delegate*). `finish()` (also called by `Drop`) later encodes the last incomplete group and adds
padding. `write` is the core method: it consumes some prefix of `input`, encodes it, and forwards it with
**at most one** call to the delegate's `write`. Its return value must follow the `io::Write::write` contract
exactly, because callers (`write_all`, retry loops) depend on it.

## 2. Functional requirements

Constants: `BUF_SIZE = 1024` (size of `self.output`), `MAX_INPUT_LEN = 768` (input bytes whose encoding fills
the buffer), `MIN_ENCODE_CHUNK_SIZE = 3`. The instance state is described in the context.

Process a call in this order:

1. If `self.finished` is true, **panic** with the message `"Cannot write more after calling finish()"`.
2. If `input` is empty, return `Ok(0)` and do nothing else.
3. **Pending output.** If `self.output_occupied_len > 0` (encoded bytes the delegate did not accept last
   time), call `self.write_to_delegate(self.output_occupied_len)` once and return `Ok(0)` if it succeeded (no
   input is consumed in this call) or its `Err` unchanged.
4. **Short input / leftover bytes.** Let `e = self.extra_input_occupied_len` (0, 1 or 2 bytes held from earlier
   calls in `self.extra_input`).
   - `e == 0` and `input.len() < 3`: copy `input` into `self.extra_input`, set `e = input.len()`, return
     `Ok(input.len())` (nothing is sent to the delegate).
   - `e > 0` and `e + input.len() < 3` (so `e == 1` and one input byte): append that byte to `extra_input`,
     set `e = 2`, return `Ok(1)`.
   - `e > 0` and `e + input.len() >= 3`: take the first `3 - e` bytes of `input` to complete the 3-byte group
     in `extra_input`; its 4 encoded symbols go first in the output buffer, and `e` becomes 0.
5. **Encode.** From the remaining input, take the largest multiple of 3 bytes that does not exceed the
   room left: at most 768 bytes, or 765 if a leftover group was completed in step 4 (so the encoded output never
   exceeds 1024 bytes). Bytes beyond the last whole group are **not** consumed and are **not** stored.
   Encoding uses `self.config`'s alphabet with no padding (`encode_to_slice` with
   `self.config.char_set.encode_table()`), appended after any symbols from step 4.
6. **Forward.** Call `self.write_to_delegate(total_encoded_len)` once (even if it is 4 bytes only).
   - On `Ok`: return `Ok(bytes_taken_to_complete_extra + bytes_encoded_from_input)`. This is the number of
     input bytes consumed, even if the delegate accepted only part of the encoded data (`write_to_delegate`
     keeps the rest in `self.output` and sets `output_occupied_len`).
   - On `Err(err)`: the call must behave as if nothing happened: restore `extra_input_occupied_len` to its
     value at the start of the call (the original leftover bytes in `extra_input` must still be intact) and
     return `Err(err)`, so that the caller can retry with the same input.

Examples (delegate = `Cursor<Vec<u8>>` that accepts everything; `URL_SAFE` or `STANDARD_NO_PAD`):

| writes (returned value) | delegate content after the encoder is dropped/finished |
|---|---|
| `"abc"` (3) | `encode("abc")` = `"YWJj"` |
| `"abcdef"` (6), `"ghi"` (3) | `encode("abcdefghi")` |
| `"a"` (1), `"bc"` (2) | `encode("abc")` |
| `"a"` (1), `"bcdef"` (5) | `encode("abcdef")` |
| `"a"` (1), `"bc"` (2), `"def"` (3) | `encode("abcdef")` |
| `"a"` (1), `"bc"` (2), `"def"` (3), `"g"` (1), then flush/drop | `encode("abcdefg")` (padded for `URL_SAFE`) |
| `"abcd"` (3), finish | `"YWJj"` (`"d"` was not consumed) |
| `"a"` (1), `"bcd"` (2), finish | `"YWJj"` |
| `"a"` (1), `"bcdefe"` (5), finish | `encode("abcdef")`, 8 bytes |
| `"ab"` (2), finish | `"YWI"` (3 bytes, no padding config) |

## 3. Input specification

- `self`: an `EncoderWriter` created by `new(w, config)`, possibly after earlier `write`s; its fields satisfy
  `extra_input_occupied_len < 3` and `output_occupied_len <= 1024`.
- `input: &[u8]`: any length (0 to megabytes).
- The delegate `W: Write` may accept only part of what it is given, return `Ok(0)`, or fail (e.g. with
  `ErrorKind::Interrupted`); callers retry after errors.

## 4. Output specification

- `Ok(n)`: `n` input bytes (a prefix of `input`) have been taken over by the encoder, as defined above; `n` may
  be 0 (pending output case) and may be less than `input.len()`.
- `Err(e)`: an error from the delegate, returned unchanged; no input is considered consumed.
- Side effects: at most one delegate `write` call; updates `extra_input`, `extra_input_occupied_len`, `output`,
  `output_occupied_len` (through `write_to_delegate`). `finished` is never changed by `write`.

## 5. Edge cases and constraints

- Any sequence of writes (all splits of the input, random sizes 0..2048, partial delegate writes and random
  `Interrupted` errors retried by the caller), followed by `finish()`, must produce exactly
  `encode_config(all_input, config)` in the delegate.
- The 1024-byte buffer must never overflow; no heap allocation.
- Never encode a trailing partial group in `write` (only `finish` does that), and never call the delegate more
  than once per `write`.

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/write/encoder.rs`
- **Enclosing scope:** `impl<'a, W: Write> Write for EncoderWriter<'a, W>`

## Imports / includes available in this file

```
use crate::encode::encode_to_slice;
use crate::{encode_config_slice, Config};
use std::{
    cmp, fmt,
    io::{ErrorKind, Result, Write},
};
```

## Other functions defined in the same file (signatures only; you may call them)

```
drop & mut self
finish & mut self
flush & mut self
fmt & self , f : & mut fmt :: Formatter
new w : & a mut W , config : Config
write_all_encoded_output & mut self
write_to_delegate & mut self , current_output_len : usize
```

## Instance state (`struct EncoderWriter<'a, W: 'a + Write>`)

```
config: Config,                                 // alphabet (config.char_set) and padding flag; Copy
w: &'a mut W,                                   // the delegate writer
extra_input: [u8; MIN_ENCODE_CHUNK_SIZE],       // up to 2 input bytes held over from earlier writes
extra_input_occupied_len: usize,                // how many bytes of extra_input are in use (0..=2 between calls)
output: [u8; BUF_SIZE],                         // encode buffer; may start with encoded bytes not yet accepted by w
output_occupied_len: usize,                     // length of that not-yet-written encoded data (0 if none)
finished: bool,                                 // set by finish(); writing afterwards is a bug
panicked: bool,                                 // maintained by write_to_delegate (panic safety for Drop)
```

Module constants:

```
pub(crate) const BUF_SIZE: usize = 1024;
const MAX_INPUT_LEN: usize = BUF_SIZE / 4 * 3;   // 768
const MIN_ENCODE_CHUNK_SIZE: usize = 3;
```

## Sibling methods and helpers

- `fn write_to_delegate(&mut self, current_output_len: usize) -> io::Result<()>`: makes exactly one
  `self.w.write(&self.output[..current_output_len])` call. On `Ok(consumed)` it sets `output_occupied_len` to
  the number of bytes not consumed and moves them to the start of `self.output` (0 if all were consumed). On
  `Err` it returns the error and leaves `output_occupied_len` unchanged.
- `fn write_all_encoded_output(&mut self) -> io::Result<()>`: writes all pending output, retrying on
  `Interrupted`.
- `pub fn finish(&mut self) -> io::Result<()>`: writes pending output, then encodes the 0-2 bytes in
  `extra_input` with padding (per `config`) and writes them; sets `finished`. `Drop` calls it.
- `encode_to_slice(input: &[u8], output: &mut [u8], encode_table: &[u8; 64]) -> usize` (imported): encodes
  without padding into the start of `output`, returns bytes written.
- `self.config.char_set.encode_table() -> &'static [u8; 64]`.

=== STUB ===
```rust
fn write(&mut self, input: &[u8]) -> Result<usize> {
    // TODO: implement according to the specification
}
```
