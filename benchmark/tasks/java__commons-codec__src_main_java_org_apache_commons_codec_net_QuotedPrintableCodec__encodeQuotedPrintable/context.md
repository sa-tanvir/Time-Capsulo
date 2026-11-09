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
