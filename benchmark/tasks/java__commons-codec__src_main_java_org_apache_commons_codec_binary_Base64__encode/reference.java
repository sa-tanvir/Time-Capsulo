void encode(final byte[] in, int inPos, final int inAvail, final Context context) {
    if (context.eof) {
        return;
    }
    // inAvail < 0 is how we're informed of EOF in the underlying data we're
    // encoding.
    if (inAvail < 0) {
        context.eof = true;
        if (0 == context.modulus && lineLength == 0) {
            return; // no leftovers to process and not using chunking
        }
        final byte[] buffer = ensureBufferSize(encodeSize, context);
        final int savedPos = context.pos;
        switch (context.modulus) { // 0-2
            case 0 : // nothing to do here
                break;
            case 1 : // 8 bits = 6 + 2
                // top 6 bits:
                buffer[context.pos++] = encodeTable[(context.ibitWorkArea >> 2) & MASK_6BITS];
                // remaining 2:
                buffer[context.pos++] = encodeTable[(context.ibitWorkArea << 4) & MASK_6BITS];
                // URL-SAFE skips the padding to further reduce size.
                if (encodeTable == STANDARD_ENCODE_TABLE) {
                    buffer[context.pos++] = pad;
                    buffer[context.pos++] = pad;
                }
                break;

            case 2 : // 16 bits = 6 + 6 + 4
                buffer[context.pos++] = encodeTable[(context.ibitWorkArea >> 10) & MASK_6BITS];
                buffer[context.pos++] = encodeTable[(context.ibitWorkArea >> 4) & MASK_6BITS];
                buffer[context.pos++] = encodeTable[(context.ibitWorkArea << 2) & MASK_6BITS];
                // URL-SAFE skips the padding to further reduce size.
                if (encodeTable == STANDARD_ENCODE_TABLE) {
                    buffer[context.pos++] = pad;
                }
                break;
            default:
                throw new IllegalStateException("Impossible modulus "+context.modulus);
        }
        context.currentLinePos += context.pos - savedPos; // keep track of current line position
        // if currentPos == 0 we are at the start of a line, so don't add CRLF
        if (lineLength > 0 && context.currentLinePos > 0) {
            System.arraycopy(lineSeparator, 0, buffer, context.pos, lineSeparator.length);
            context.pos += lineSeparator.length;
        }
    } else {
        for (int i = 0; i < inAvail; i++) {
            final byte[] buffer = ensureBufferSize(encodeSize, context);
            context.modulus = (context.modulus+1) % BYTES_PER_UNENCODED_BLOCK;
            int b = in[inPos++];
            if (b < 0) {
                b += 256;
            }
            context.ibitWorkArea = (context.ibitWorkArea << 8) + b; //  BITS_PER_BYTE
            if (0 == context.modulus) { // 3 bytes = 24 bits = 4 * 6 bits to extract
                buffer[context.pos++] = encodeTable[(context.ibitWorkArea >> 18) & MASK_6BITS];
                buffer[context.pos++] = encodeTable[(context.ibitWorkArea >> 12) & MASK_6BITS];
                buffer[context.pos++] = encodeTable[(context.ibitWorkArea >> 6) & MASK_6BITS];
                buffer[context.pos++] = encodeTable[context.ibitWorkArea & MASK_6BITS];
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
