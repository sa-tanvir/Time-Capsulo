You are an expert Java developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Java code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```java code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/binary/Base32.java`
- **Enclosing scope:** `public class Base32 extends BaseNCodec`

## Imports / includes available in this file

```
(none)
```

## Other functions defined in the same file (signatures only; you may call them)

```
Base32::Base32( final boolean useHex , final byte pad)
Base32::Base32( final boolean useHex)
Base32::Base32( final byte pad)
Base32::Base32( final int lineLength , final byte [ ] lineSeparator , final boolean useHex , final byte pad)
Base32::Base32( final int lineLength , final byte [ ] lineSeparator , final boolean useHex)
Base32::Base32( final int lineLength , final byte [ ] lineSeparator)
Base32::Base32( final int lineLength)
Base32::Base32()
Base32::decode( final byte [ ] in , int inPos , final int inAvail , final Context context)
Base32::isInAlphabet( final byte octet)
Base32::validateCharacter( final int numBits , final Context context)
```

## Instance state

Fields of the `Base32` instance read by `encode`:
- `encodeTable` (`byte[]`, 32 entries): the alphabet used for output; `ENCODE_TABLE` (`A-Z 2-7`) or `HEX_ENCODE_TABLE` (`0-9 A-V`).
- `lineLength` (`int`, from `BaseNCodec`): 0 if no line chunking, otherwise the line length in output characters (a multiple of 8).
- `lineSeparator` (`byte[]`): the separator bytes written between lines (only meaningful when `lineLength > 0`).
- `pad` (`byte`, from `BaseNCodec`): the padding byte (default `'='`).
- `encodeSize` (`int`): `8 + lineSeparator.length` (or 8 without chunking): upper bound on the bytes written for one input group.
- `BYTES_PER_UNENCODED_BLOCK = 5`, `BYTES_PER_ENCODED_BLOCK = 8`, `MASK_5BITS = 0x1f`.

`BaseNCodec.Context` (package-private static class; fields are package-private and may be read and written):
- `long lbitWorkArea`: accumulated bits of the pending (incomplete) input group (Base32 uses this one).
- `int ibitWorkArea`: same as an `int` (used by Base64).
- `byte[] buffer`: output bytes, `null` until first needed.
- `int pos`: next write position in `buffer`; `int readPos`: next read position (not used by `encode`).
- `boolean eof`: end of input has been signalled.
- `int currentLinePos`: characters already written on the current output line.
- `int modulus`: number of input bytes of the current group already consumed (0..4).

Helper in `BaseNCodec`: `protected byte[] ensureBufferSize(int size, Context context)` makes sure that at least `size` more bytes fit in `context.buffer` at `context.pos` (allocating the buffer if it is `null` and doubling it otherwise, keeping the old content) and returns the (possibly new) buffer; call it again after each group so that the local reference is current.

=== STUB ===
```java
void encode(final byte[] in, int inPos, final int inAvail, final Context context) {
    // TODO: implement according to the specification
}
```
