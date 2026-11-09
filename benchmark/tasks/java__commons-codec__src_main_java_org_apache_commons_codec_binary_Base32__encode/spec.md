# Functional specification

## 1. Component overview

`Base32.encode(byte[] in, int inPos, int inAvail, Context context)` is the incremental (streaming) encoder of the `Base32` codec. It is called repeatedly with successive chunks of input bytes, and once with `inAvail < 0` to signal the end of the input. The encoded text is accumulated in the `context` object (see "Instance state"); the method returns nothing.

## 2. Functional requirements

1. If `context.eof` is already `true`, return immediately without any change.
2. **Data call** (`inAvail >= 0`): consume the `inAvail` bytes `in[inPos .. inPos+inAvail-1]`. Bytes are treated as unsigned (0..255). The call may begin in the middle of a 5-byte group: the `context` remembers how many bytes of the current group have been seen (`context.modulus`, cycling 0..4) and their accumulated bits, so that the output is the same regardless of how the input is split into calls. Each time a complete group of 5 input bytes has been collected, 8 output characters are appended to `context.buffer` (at `context.pos`, which advances), each representing 5 bits of the group, most significant bits first, taken from the 32-character Base32 alphabet (`A-Z 2-7`) or the extended-hex alphabet (`0-9 A-V`) as selected by the instance. `context.currentLinePos` counts the characters written on the current line; after each group of 8 characters, if the instance uses line chunking (`lineLength > 0`) and `currentLinePos` has reached `lineLength`, the line separator bytes of the instance are appended and `currentLinePos` is reset to 0.
3. **End-of-input call** (`inAvail < 0`): set `context.eof = true`. Then, if no bytes are pending (`context.modulus == 0`) and the instance does not use line chunking (`lineLength == 0`), nothing is appended. Otherwise the pending bytes (if any) are encoded as a final partial group: their bits are left-aligned into 5-bit characters and the last character is zero-padded on the right; then padding is applied as described below; `currentLinePos` is increased by the number of characters written by this call; finally, if the instance uses line chunking and `currentLinePos > 0` (the current line is not empty), the line separator is appended once.
   - 1 pending byte: 2 characters followed by 6 pad bytes; 2 pending bytes: 4 characters followed by 4 pad bytes; 3 pending bytes: 5 characters followed by 3 pad bytes; 4 pending bytes: 7 characters followed by 1 pad byte. Padding bytes are the instance's pad byte (default `=`) and are always written (for both alphabets), so a final group always has 8 output bytes.
4. The output buffer is created and grown on demand (see `ensureBufferSize` in the context); callers only look at `context.buffer[0 .. context.pos-1]`. Existing buffer content is preserved when it grows.

## 3. Input specification

- `in`: byte array (may be `null` for the end-of-input call).
- `inPos`, `inAvail`: start offset and number of bytes (`inAvail < 0` means end of input). `inAvail == 0` consumes nothing (but does not set `eof`).
- `context`: a `Context` whose state is carried over between calls; fresh contexts start with `modulus = 0`, `pos = 0`, `currentLinePos = 0`, `eof = false`, `buffer = null`.

## 4. Output specification

The context is updated in place: new output bytes are written to `context.buffer` starting at the previous `context.pos`; `pos`, `modulus`, the work area, `currentLinePos` and `eof` are updated. Example (standard alphabet, no chunking, one data call with the bytes of `"abc"` followed by an end-of-input call): `buffer[0..pos-1]` is the ASCII text `MFRGG===`. The same bytes fed in three data calls of one byte each give the same result.

## 5. Edge cases and constraints

- Calls after `eof` is set are ignored (no output, no exception).
- With line chunking, a separator is written after every full line, and one extra separator ends the final non-empty line at end of input; if the last full line has just been terminated (`currentLinePos == 0`), no extra separator is written.
- `IllegalStateException` with message `Impossible modulus <n>` is thrown if the pending-byte count is not one of the possible values (cannot happen with a valid context).
- Not thread-safe; all mutable state is in the `context`.
