# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/binary/Base64.java`
- **Enclosing scope:** `public class Base64 extends BaseNCodec`

## Imports / includes available in this file

```
import java.math.BigInteger;
```

## Other functions defined in the same file (signatures only; you may call them)

```
Base64::Base64( final boolean urlSafe)
Base64::Base64( final int lineLength , final byte [ ] lineSeparator , final boolean urlSafe)
Base64::Base64( final int lineLength , final byte [ ] lineSeparator)
Base64::Base64( final int lineLength)
Base64::Base64()
Base64::decode( final byte [ ] in , int inPos , final int inAvail , final Context context)
Base64::decodeBase64( final String base64String)
Base64::decodeBase64( final byte [ ] base64Data)
Base64::decodeInteger( final byte [ ] pArray)
Base64::encodeBase64( final byte [ ] binaryData , final boolean isChunked , final boolean urlSafe , final int maxResultSize)
Base64::encodeBase64( final byte [ ] binaryData , final boolean isChunked , final boolean urlSafe)
Base64::encodeBase64( final byte [ ] binaryData , final boolean isChunked)
Base64::encodeBase64( final byte [ ] binaryData)
Base64::encodeBase64Chunked( final byte [ ] binaryData)
Base64::encodeBase64String( final byte [ ] binaryData)
Base64::encodeBase64URLSafe( final byte [ ] binaryData)
Base64::encodeBase64URLSafeString( final byte [ ] binaryData)
Base64::encodeInteger( final BigInteger bigInt)
Base64::isArrayByteBase64( final byte [ ] arrayOctet)
Base64::isBase64( final String base64)
Base64::isBase64( final byte [ ] arrayOctet)
Base64::isBase64( final byte octet)
Base64::isInAlphabet( final byte octet)
Base64::isUrlSafe()
Base64::toIntegerBytes( final BigInteger bigInt)
Base64::validateCharacter( final int numBitsToDrop , final Context context)
```

## Instance state

Fields of the `Base64` instance read by `encode`:
- `encodeTable` (`byte[]`, 64 entries): the alphabet used for output; either `STANDARD_ENCODE_TABLE` (`A-Z a-z 0-9 + /`) or `URL_SAFE_ENCODE_TABLE` (`A-Z a-z 0-9 - _`). Compare with `==` against `STANDARD_ENCODE_TABLE` to know whether padding applies.
- `lineLength` (`int`, from `BaseNCodec`): 0 if no line chunking, otherwise the line length in output characters (a multiple of 4).
- `lineSeparator` (`byte[]`): the separator bytes written between lines (only meaningful when `lineLength > 0`).
- `pad` (`byte`, from `BaseNCodec`): the padding byte (default `'='`).
- `encodeSize` (`int`): `4 + lineSeparator.length` (or 4 without chunking): upper bound on the bytes written for one input group.
- `BYTES_PER_UNENCODED_BLOCK = 3`, `BYTES_PER_ENCODED_BLOCK = 4`, `MASK_6BITS = 0x3f`.

`BaseNCodec.Context` (package-private static class; fields are package-private and may be read and written):
- `int ibitWorkArea`: accumulated bits of the pending (incomplete) input group (Base64 uses this one).
- `long lbitWorkArea`: same as a `long` (used by Base32).
- `byte[] buffer`: output bytes, `null` until first needed.
- `int pos`: next write position in `buffer`; `int readPos`: next read position (not used by `encode`).
- `boolean eof`: end of input has been signalled.
- `int currentLinePos`: characters already written on the current output line.
- `int modulus`: number of input bytes of the current group already consumed (0..2).

Helper in `BaseNCodec`: `protected byte[] ensureBufferSize(int size, Context context)` makes sure that at least `size` more bytes fit in `context.buffer` at `context.pos` (allocating the buffer if it is `null` and doubling it otherwise, keeping the old content) and returns the (possibly new) buffer; call it again after each group so that the local reference is current.
