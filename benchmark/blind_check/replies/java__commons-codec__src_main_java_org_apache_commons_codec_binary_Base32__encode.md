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
        final long w = context.lbitWorkArea;
        int padCount;
        switch (context.modulus) {
        case 0:
            padCount = 0;
            break;
        case 1:
            buffer[context.pos++] = encodeTable[(int) (w >> 3) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w << 2) & MASK_5BITS];
            padCount = 6;
            break;
        case 2:
            buffer[context.pos++] = encodeTable[(int) (w >> 11) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 6) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 1) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w << 4) & MASK_5BITS];
            padCount = 4;
            break;
        case 3:
            buffer[context.pos++] = encodeTable[(int) (w >> 19) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 14) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 9) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 4) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w << 1) & MASK_5BITS];
            padCount = 3;
            break;
        case 4:
            buffer[context.pos++] = encodeTable[(int) (w >> 27) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 22) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 17) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 12) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 7) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w >> 2) & MASK_5BITS];
            buffer[context.pos++] = encodeTable[(int) (w << 3) & MASK_5BITS];
            padCount = 1;
            break;
        default:
            throw new IllegalStateException("Impossible modulus " + context.modulus);
        }
        for (int i = 0; i < padCount; i++) {
            buffer[context.pos++] = pad;
        }
        context.currentLinePos += context.pos - savedPos;
        if (lineLength > 0 && context.currentLinePos > 0) {
            System.arraycopy(lineSeparator, 0, buffer, context.pos, lineSeparator.length);
            context.pos += lineSeparator.length;
        }
    } else {
        for (int i = 0; i < inAvail; i++) {
            final byte[] buffer = ensureBufferSize(encodeSize, context);
            context.modulus = (context.modulus + 1) % 5;
            int b = in[inPos++];
            if (b < 0) {
                b += 256;
            }
            context.lbitWorkArea = (context.lbitWorkArea << 8) + b;
            if (0 == context.modulus) {
                final long w = context.lbitWorkArea;
                buffer[context.pos++] = encodeTable[(int) (w >> 35) & MASK_5BITS];
                buffer[context.pos++] = encodeTable[(int) (w >> 30) & MASK_5BITS];
                buffer[context.pos++] = encodeTable[(int) (w >> 25) & MASK_5BITS];
                buffer[context.pos++] = encodeTable[(int) (w >> 20) & MASK_5BITS];
                buffer[context.pos++] = encodeTable[(int) (w >> 15) & MASK_5BITS];
                buffer[context.pos++] = encodeTable[(int) (w >> 10) & MASK_5BITS];
                buffer[context.pos++] = encodeTable[(int) (w >> 5) & MASK_5BITS];
                buffer[context.pos++] = encodeTable[(int) w & MASK_5BITS];
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
