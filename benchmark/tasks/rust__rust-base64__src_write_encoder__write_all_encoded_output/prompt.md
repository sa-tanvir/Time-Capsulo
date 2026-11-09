You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context, but do not add new imports or helper functions;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `EncoderWriter::write_all_encoded_output(&mut self) -> io::Result<()>`

## 1. Component overview

Part of the `base64` crate (v0.11), module `write`. `EncoderWriter<'a, W>` base64-encodes data written to it and
forwards the encoded text to a wrapped writer `self.w` (the *delegate*). Encoded bytes the delegate has not yet
accepted are kept at the start of `self.output`, and `self.output_occupied_len` says how many there are.
`write_all_encoded_output` pushes **all** of that pending encoded data to the delegate. It is used by `finish()`
(before and after encoding the final partial group with padding, and therefore by `Drop`) and by `flush()`.
It is like `Write::write_all` for the pending buffer, but it does **not** treat `Ok(0)` from the delegate as an
error, and it retries `Interrupted` errors.

## 2. Functional requirements

1. While `self.output_occupied_len > 0`, perform one delegate write through the sibling method
   `self.write_to_delegate(self.output_occupied_len)` (which writes `output[..len]` once, and on success moves
   the unaccepted remainder to the front of `output` and updates `output_occupied_len`).
2. If that call returns an error whose kind is `ErrorKind::Interrupted`, ignore it and try again.
3. If it returns any other error, stop immediately and return that error unchanged; `output_occupied_len`
   keeps the value it had before the failing call (nothing is discarded, so a later retry can continue).
4. If it succeeds (including when the delegate accepted 0 bytes), continue the loop.
5. When nothing is pending (`output_occupied_len == 0`), return `Ok(())`. If nothing was pending on entry, return
   `Ok(())` without calling the delegate at all.

Postcondition of `Ok(())`: `self.output_occupied_len == 0`, and the delegate has received exactly the pending
bytes, in order, with no duplication or loss.

Example: pending `"YWJjZGVm"` (8 bytes) and a delegate that accepts at most 3 bytes per call and returns
`Interrupted` on its 2nd call. Calls: accept `"YWJ"` (pending 5), `Interrupted` (retry), accept `"jZG"` (pending 2),
accept `"Vm"` (pending 0), return `Ok(())`. The delegate holds `"YWJjZGVm"` after 4 calls.

Behaviour observed by the tests: every `EncoderWriter` round trip (`write`/`write_all` in any split, `flush()`,
`finish()`, `Drop`) must deliver exactly `encode_config(all_input, config)` to the delegate, also when the
delegate randomly accepts only a prefix of each buffer or returns `Interrupted` most of the time.

## 3. Input specification

- `&mut self`: an `EncoderWriter` whose first `output_occupied_len` (0..=1024) bytes of `output` are pending
  encoded data. The other fields are not involved (see the instance state in the context).
- The delegate `W: Write` may accept any prefix of each buffer (possibly 0 bytes), and may fail with any
  `io::Error`.

## 4. Output specification

- `Ok(())` once all pending bytes are written (`output_occupied_len == 0`).
- `Err(e)` for the first delegate error that is not `Interrupted`, returned as is.
- No other state than `output`, `output_occupied_len` and `panicked` (all maintained by `write_to_delegate`) is
  changed; input-related fields (`extra_input`, `extra_input_occupied_len`, `finished`) are untouched.

## 5. Edge cases and constraints

- Nothing pending: no delegate call, `Ok(())`.
- A delegate that keeps returning `Ok(0)` or `Interrupted` makes the method keep trying (it does not give up).
- Every delegate call goes through `write_to_delegate`, one at a time; no heap allocation.

=== CONTEXT ===
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

=== STUB ===
```rust
fn write_all_encoded_output(&mut self) -> Result<()> {
    // TODO: implement according to the specification
}
```
