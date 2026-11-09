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
