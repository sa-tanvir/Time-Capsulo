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

`QuotedPrintableCodec.encodeQuotedPrintable(BitSet printable, byte[] bytes, boolean strict)` encodes bytes in the Quoted-Printable transfer encoding of RFC 1521 (MIME). Bytes in the "printable" set are written as they are; all other bytes are written as an escape `=` followed by two upper-case hexadecimal digits. In strict mode the output additionally follows the RFC's line-length and white-space rules by inserting soft line breaks.

## 2. Functional requirements

1. If `bytes` is `null`, return `null`.
2. If `printable` is `null`, use the codec's default printable set `PRINTABLE_CHARS` (see context).
3. Every input byte is treated as an unsigned value 0..255 (`b < 0` becomes `256 + b`), and "is printable" means `printable.get(value)`.
4. **Non-strict mode** (`strict == false`): each byte that is in the printable set is copied; each other byte is replaced by `=XY` (`X`, `Y` the upper-case hex digits of the unsigned value, e.g. `=0D`, `=C3`). No line breaks are inserted. Return the resulting bytes.
5. **Strict mode** (`strict == true`), for input of at least three bytes. The output is built with a running column counter `pos`, starting at 1. Let `n` be the length of the input.
   - For each of the first `n - 3` bytes, in order:
     - if `pos < SAFE_LENGTH` (73): write the byte (escaped when it is not printable) and add the number of bytes written (1 or 3) to `pos`;
     - otherwise (the line is full): write the byte, escaped if it is not printable **or** is a blank (space or tab); then write a soft line break (`=` CR LF; the three bytes `=`, `\r`, `\n`) and reset `pos` to 1.
   - The third byte from the end is written escaped if it is not printable, or if it is a blank and `pos > SAFE_LENGTH - 5`; `pos` increases by the bytes written.
   - If now `pos > SAFE_LENGTH - 2`, write a soft line break (`=` CR LF).
   - The last two bytes are each written escaped if they are not printable, or, for the **final** byte only, if it is a blank (space or tab). The second-to-last byte is only escaped if it is not printable.
   - Return the resulting bytes.
6. Strict mode with fewer than three input bytes is outside the contract (the reference fails with an `ArrayIndexOutOfBoundsException`, since it reads the third byte from the end); it need not be supported.

## 3. Input specification

- `printable`: a `BitSet` over 0..255 or `null`.
- `bytes`: any byte array or `null`.
- `strict`: boolean.

## 4. Output specification

A new byte array containing the encoded ASCII text, or `null` when `bytes` is `null`. Examples (non-strict, default set): `"Hello=World"` bytes -> `Hello=3DWorld`; bytes `{0x41, 0x0D, 0x0A, 0xC3}` -> `A=0D=0A=C3`; empty array -> empty array.

## 5. Edge cases and constraints

- The inputs are not modified. Output uses upper-case hex digits only.
- A byte in a custom `printable` set is never escaped (in non-strict mode); in particular `=` is escaped only if it is not in the set.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/net/QuotedPrintableCodec.java`
- **Enclosing scope:** `public class QuotedPrintableCodec implements BinaryEncoder, BinaryDecoder, StringEncoder, StringDecoder`

## Imports / includes available in this file

```
import java.io.ByteArrayOutputStream;
import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;
import java.nio.charset.IllegalCharsetNameException;
import java.nio.charset.UnsupportedCharsetException;
import java.util.BitSet;
import org.apache.commons.codec.BinaryDecoder;
import org.apache.commons.codec.BinaryEncoder;
import org.apache.commons.codec.Charsets;
import org.apache.commons.codec.DecoderException;
import org.apache.commons.codec.EncoderException;
import org.apache.commons.codec.StringDecoder;
import org.apache.commons.codec.StringEncoder;
import org.apache.commons.codec.binary.StringUtils;
```

## Other functions defined in the same file (signatures only; you may call them)

```
QuotedPrintableCodec::QuotedPrintableCodec( final Charset charset , final boolean strict)
QuotedPrintableCodec::QuotedPrintableCodec( final Charset charset)
QuotedPrintableCodec::QuotedPrintableCodec( final String charsetName)
QuotedPrintableCodec::QuotedPrintableCodec( final boolean strict)
QuotedPrintableCodec::QuotedPrintableCodec()
QuotedPrintableCodec::decode( final Object obj)
QuotedPrintableCodec::decode( final String sourceStr , final Charset sourceCharset)
QuotedPrintableCodec::decode( final String sourceStr , final String sourceCharset)
QuotedPrintableCodec::decode( final String sourceStr)
QuotedPrintableCodec::decode( final byte [ ] bytes)
QuotedPrintableCodec::decodeQuotedPrintable( final byte [ ] bytes)
QuotedPrintableCodec::encode( final Object obj)
QuotedPrintableCodec::encode( final String sourceStr , final Charset sourceCharset)
QuotedPrintableCodec::encode( final String sourceStr , final String sourceCharset)
QuotedPrintableCodec::encode( final String sourceStr)
QuotedPrintableCodec::encode( final byte [ ] bytes)
QuotedPrintableCodec::encodeByte( final int b , final boolean encode , final ByteArrayOutputStream buffer)
QuotedPrintableCodec::encodeQuotedPrintable( final BitSet printable , final byte [ ] bytes)
QuotedPrintableCodec::encodeQuotedPrintable( final int b , final ByteArrayOutputStream buffer)
QuotedPrintableCodec::for( int i = 33 ; i <= 60 ; i ++)
QuotedPrintableCodec::for( int i = 62 ; i <= 126 ; i ++)
QuotedPrintableCodec::getCharset()
QuotedPrintableCodec::getDefaultCharset()
QuotedPrintableCodec::getUnsignedOctet( final int index , final byte [ ] bytes)
QuotedPrintableCodec::isWhitespace( final int b)
```

## Constants and helpers

```
private static final BitSet PRINTABLE_CHARS = new BitSet(256); // bits 33..60, 62..126, 9 (TAB) and 32 (SPACE) are set
private static final byte ESCAPE_CHAR = '=';
private static final byte TAB = 9;
private static final byte SPACE = 32;
private static final byte CR = 13;
private static final byte LF = 10;
private static final int SAFE_LENGTH = 73;

private static final int encodeQuotedPrintable(final int b, final ByteArrayOutputStream buffer) // writes '=' and two upper-case hex digits; returns 3
private static int getUnsignedOctet(final int index, final byte[] bytes) // bytes[index] as 0..255
private static int encodeByte(final int b, final boolean encode, final ByteArrayOutputStream buffer) // writes escaped (returns 3) or raw (returns 1)
private static boolean isWhitespace(final int b) // true for SPACE or TAB
```

=== STUB ===
```java
public static final byte[] encodeQuotedPrintable(BitSet printable, final byte[] bytes, final boolean strict) {
    // TODO: implement according to the specification
}
```
