Workload: 300 streams per size (S: 0-200 bytes written in pieces of 0-10 bytes; M: 2-8 KB in pieces up to 10-300;
L: 20-80 KB in pieces up to 100-3000, i.e. beyond the 768-byte per-call limit), random alphabet and padding. Half
the streams use a delegate that accepts everything; the others accept at most 1-1100 bytes per call and/or fail
with `Interrupted` on every 2nd-7th call. Data and the cyclic piece-size list are generated from a seed by the driver.
Invocation: `driver.rs` is appended to `src/write/encoder.rs` of a container-local copy (`/tmp/w`) and run with
`cargo test --release`; per stream it creates an `EncoderWriter`, calls `write` until all data is consumed
(retrying errors) and then `finish()`. `check` hashes every `write` result and the delegate's bytes (FNV-1a 64).
