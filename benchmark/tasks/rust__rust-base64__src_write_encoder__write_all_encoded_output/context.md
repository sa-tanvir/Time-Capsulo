# Context for the function to implement

- **Language:** rust
- **File:** `src/write/encoder.rs`
- **Enclosing scope:** `impl<'a, W: Write> EncoderWriter<'a, W>`

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
write & mut self , input : & [ u8 ]
write_to_delegate & mut self , current_output_len : usize
```

## Instance state (`struct EncoderWriter<'a, W: 'a + Write>`)

```
config: Config,                                 // alphabet and padding flag
w: &'a mut W,                                   // the delegate writer
extra_input: [u8; MIN_ENCODE_CHUNK_SIZE],       // up to 2 not-yet-encoded input bytes (not used here)
extra_input_occupied_len: usize,                // (not used here)
output: [u8; BUF_SIZE],                         // starts with encoded bytes not yet accepted by w
output_occupied_len: usize,                     // number of such pending bytes (0 if none)
finished: bool,                                 // set by finish() (not used here)
panicked: bool,                                 // maintained by write_to_delegate
```

Module constants: `BUF_SIZE = 1024`, `MAX_INPUT_LEN = 768`, `MIN_ENCODE_CHUNK_SIZE = 3`.

## Sibling method

- `fn write_to_delegate(&mut self, current_output_len: usize) -> io::Result<()>`: makes exactly one
  `self.w.write(&self.output[..current_output_len])` call. On `Ok(consumed)` it sets `output_occupied_len` to
  `current_output_len - consumed` and moves the unconsumed bytes to the start of `self.output`. On `Err` it
  returns the error and leaves `output_occupied_len` unchanged.
- `ErrorKind` (imported) distinguishes `ErrorKind::Interrupted` from other `io::Error` kinds (`e.kind()`).
