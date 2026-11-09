Workload: 300 cases per size. Each case is a pending encoded buffer (S: 0-64 bytes, M: 256-1024, L: 1000-1024) and a
delegate that accepts at most `cap` bytes per call (S: 0-64 with 0 = everything, M: 16-96, L: 1-6, so L needs hundreds
of delegate calls) and sometimes accepts 0 bytes, fails with `Interrupted` periodically, or fails once with
`ErrorKind::Other`. Pending bytes are generated from a seed by the driver.
Invocation: `driver.rs` is appended to `src/write/encoder.rs` of a container-local copy (`/tmp/w`) and run with
`cargo test --release`. For each case it builds an `EncoderWriter`, fills `output`/`output_occupied_len` (outside the
timed region) and times only `write_all_encoded_output()`. `check` hashes the result, the remaining pending length,
the number of delegate calls and the delegate's bytes (FNV-1a 64).
