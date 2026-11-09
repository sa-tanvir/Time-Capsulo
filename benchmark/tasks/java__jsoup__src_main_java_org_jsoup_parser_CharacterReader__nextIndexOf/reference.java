int nextIndexOf(CharSequence seq) {
    bufferUp();
    // doesn't handle scanning for surrogates
    char startChar = seq.charAt(0);
    for (int offset = bufPos; offset < bufLength; offset++) {
        // scan to first instance of startchar:
        if (startChar != charBuf[offset])
            while(++offset < bufLength && startChar != charBuf[offset]) { /* empty */ }
        int i = offset + 1;
        int last = i + seq.length()-1;
        if (offset < bufLength && last <= bufLength) {
            for (int j = 1; i < last && seq.charAt(j) == charBuf[i]; i++, j++) { /* empty */ }
            if (i == last) // found full sequence
                return offset - bufPos;
        }
    }
    return -1;
}
