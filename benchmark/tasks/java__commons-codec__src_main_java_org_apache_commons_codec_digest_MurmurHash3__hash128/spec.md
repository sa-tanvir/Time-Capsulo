# Functional specification

## 1. Component overview

`MurmurHash3.hash128(byte[] data, int offset, int length, int seed)` computes the 128-bit MurmurHash3 (x64 variant, as published by Austin Appleby) of `length` bytes of `data` starting at `offset`, and returns it as two 64-bit words.

## 2. Functional requirements

All arithmetic is on 64-bit two's-complement `long` values and wraps silently; bytes are read as unsigned values (0..255); multi-byte groups are read **little-endian**. `rotl(x, r)` is a left rotation of a 64-bit value by `r` bits. The constants `C1`, `C2`, `R1`, `R2`, `R3`, `M`, `N1`, `N2` and the finalisation mix `fmix64(long)` are listed in the context.

1. Two state words `h1` and `h2` both start as the `seed`, sign-extended from `int` to `long`.
2. The input is consumed in blocks of 16 bytes: `length / 16` full blocks. For each block, `k1` is the little-endian 64-bit value of its first 8 bytes and `k2` that of its last 8 bytes. Then:
   - `k1` is multiplied by `C1`, rotated left by `R1` bits and multiplied by `C2`; the result is XOR-ed into `h1`; `h1` is rotated left by `R2` bits, `h2` is added to it, and it is replaced by five times itself plus `N1` (`M` is that factor).
   - `k2` is multiplied by `C2`, rotated left by `R3` bits and multiplied by `C1`; the result is XOR-ed into `h2`; `h2` is rotated left by `R1` bits, the already updated `h1` is added to it, and it is replaced by `M` times itself plus `N2`.
3. The remaining `length % 16` bytes (the tail) are combined little-endian into `k1` (tail bytes 0..7) and `k2` (tail bytes 8..14), absent bytes counting as zero. If the tail has more than 8 bytes, `k2` is mixed in like the second half of a block step (multiply by `C2`, rotate left by `R3`, multiply by `C1`) and XOR-ed into `h2` (without the rotation/addition steps of a full block). If the tail has at least 1 byte, `k1` is mixed in the same way as in a block (multiply by `C1`, rotate left by `R1`, multiply by `C2`) and XOR-ed into `h1` (again without the rotation/addition steps).
4. Finalisation: both `h1` and `h2` are XOR-ed with `length`; then `h1 += h2` and `h2 += h1`; then `h1` and `h2` are each replaced by `fmix64` of themselves; then again `h1 += h2` and `h2 += h1`.
5. Return `new long[] { h1, h2 }`.

## 3. Input specification

- `data`: non-null byte array with at least `offset + length` bytes. `offset >= 0`, `length >= 0`.
- `seed`: any `int` (negative values allowed; they are sign-extended).

## 4. Output specification

A new `long[2]` array `{h1, h2}`. An empty range (`length == 0`) is valid and hashes only the seed and length.

## 5. Edge cases and constraints

- Only the bytes `data[offset .. offset+length-1]` are read; the input is not modified.
- The result for a given `(bytes, seed)` does not depend on `offset`: hashing the same bytes at a different offset gives the same hash.
- Pure function, thread-safe.
