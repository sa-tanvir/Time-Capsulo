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
