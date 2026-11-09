Workload: S holds the literal inputs from the tests/docs (`foobar`, `foobarf`, the fast-loop strings, 0..255, ...)
for all three alphabets with and without padding plus 300 random inputs of 0-100 bytes; M holds inputs around the
765/768-byte chunk boundary plus 300 random inputs of 500-2500 bytes; L 300 random inputs of 5-25 KB. Random bytes
are generated from a seed by the driver (xorshift64*), so the files stay small.
Invocation: `driver.rs` is appended to `src/chunked_encoder.rs` of a container-local copy (`/tmp/w`) and run with
`cargo test --release`; it calls `ChunkedEncoder::new(cfg).encode(data, sink)` with a sink that appends to a
pre-reserved `Vec<u8>` (cleared outside the call). `check` hashes the concatenated output with FNV-1a 64.
