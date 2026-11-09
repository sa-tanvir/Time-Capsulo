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
