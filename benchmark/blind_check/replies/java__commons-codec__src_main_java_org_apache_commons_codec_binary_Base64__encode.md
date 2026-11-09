```java
void encode(final byte[] in, int inPos, final int inAvail, final Context context) {
    if (context.eof) {
        return;
    }
    if (inAvail < 0) {
        context.eof = true;
        if (0 == context.modulus && lineLength == 0) {
            return;
        }
        final byte[] buffer = ensureBufferSize(encodeSize, context);
        final int savedPos = context.pos;
        final int w = context.ibitWorkArea;
        switch (context.modulus) {
        case 0:
            break;
        case 1:
            buffer[context.pos++] = encodeTable[(w >> 2) & MASK_6BITS];
            buffer[context.pos++] = encodeTable[(w << 4) & MASK_6BITS];
            if (encodeTable == STANDARD_ENCODE_TABLE) {
                buffer[context.pos++] = pad;
                buffer[context.pos++] = pad;
            }
            break;
        case 2:
            buffer[context.pos++] = encodeTable[(w >> 10) & MASK_6BITS];
            buffer[context.pos++] = encodeTable[(w >> 4) & MASK_6BITS];
            buffer[context.pos++] = encodeTable[(w << 2) & MASK_6BITS];
            if (encodeTable == STANDARD_ENCODE_TABLE) {
                buffer[context.pos++] = pad;
            }
            break;
        default:
            throw new IllegalStateException("Impossible modulus " + context.modulus);
        }
        context.currentLinePos += context.pos - savedPos;
        if (lineLength > 0 && context.currentLinePos > 0) {
            System.arraycopy(lineSeparator, 0, buffer, context.pos, lineSeparator.length);
            context.pos += lineSeparator.length;
        }
    } else {
        for (int i = 0; i < inAvail; i++) {
            final byte[] buffer = ensureBufferSize(encodeSize, context);
            context.modulus = (context.modulus + 1) % 3;
            int b = in[inPos++];
            if (b < 0) {
                b += 256;
            }
            context.ibitWorkArea = (context.ibitWorkArea << 8) + b;
            if (0 == context.modulus) {
                final int w = context.ibitWorkArea;
                buffer[context.pos++] = encodeTable[(w >> 18) & MASK_6BITS];
                buffer[context.pos++] = encodeTable[(w >> 12) & MASK_6BITS];
                buffer[context.pos++] = encodeTable[(w >> 6) & MASK_6BITS];
                buffer[context.pos++] = encodeTable[w & MASK_6BITS];
                context.currentLinePos += BYTES_PER_ENCODED_BLOCK;
                if (lineLength > 0 && lineLength <= context.currentLinePos) {
                    System.arraycopy(lineSeparator, 0, buffer, context.pos, lineSeparator.length);
                    context.pos += lineSeparator.length;
                    context.currentLinePos = 0;
                }
            }
        }
    }
}
```
