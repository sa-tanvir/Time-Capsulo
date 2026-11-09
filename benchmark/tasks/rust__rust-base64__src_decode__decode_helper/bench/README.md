Workload: S holds the literal inputs from the decode tests (RFC 4648 vectors, bad padding, invalid bytes, invalid
last symbols) for all three alphabets, with and without `decode_allow_trailing_bits`, plus 300 random cases of 0-100 raw
bytes; M and L hold 500 random cases of 300-700 and 3000-7000 raw bytes. Random cases are generated from a seed by the
driver and encoded with the crate's `encode_config` (padded or not); ~15% get one corrupted byte or a truncated tail.
Invocation: `driver.rs` is appended to `src/decode.rs` of a container-local copy (`/tmp/w`) and run with
`cargo test --release`; it calls `decode_helper(input, num_chunks(input), config, out)` with `out` sized like
`decode_config_buf` does. Inputs are built before timing; `check` hashes results and error values with FNV-1a 64.
