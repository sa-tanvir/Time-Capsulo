```java
public static final byte[] encodeQuotedPrintable(BitSet printable, final byte[] bytes, final boolean strict) {
    if (bytes == null) {
        return null;
    }
    if (printable == null) {
        printable = PRINTABLE_CHARS;
    }
    final ByteArrayOutputStream buffer = new ByteArrayOutputStream();
    if (strict) {
        int pos = 1;
        for (int i = 0; i < bytes.length - 3; i++) {
            final int b = getUnsignedOctet(i, bytes);
            if (pos < SAFE_LENGTH) {
                pos += encodeByte(b, !printable.get(b), buffer);
            } else {
                encodeByte(b, !printable.get(b) || isWhitespace(b), buffer);
                buffer.write(ESCAPE_CHAR);
                buffer.write(CR);
                buffer.write(LF);
                pos = 1;
            }
        }
        int b = getUnsignedOctet(bytes.length - 3, bytes);
        boolean encode = !printable.get(b) || (isWhitespace(b) && pos > SAFE_LENGTH - 5);
        pos += encodeByte(b, encode, buffer);
        if (pos > SAFE_LENGTH - 2) {
            buffer.write(ESCAPE_CHAR);
            buffer.write(CR);
            buffer.write(LF);
        }
        for (int i = bytes.length - 2; i < bytes.length; i++) {
            b = getUnsignedOctet(i, bytes);
            encode = !printable.get(b) || (i > bytes.length - 2 && isWhitespace(b));
            encodeByte(b, encode, buffer);
        }
    } else {
        for (final byte c : bytes) {
            int b = c;
            if (b < 0) {
                b = 256 + b;
            }
            if (printable.get(b)) {
                buffer.write(b);
            } else {
                encodeQuotedPrintable(b, buffer);
            }
        }
    }
    return buffer.toByteArray();
}
```
