```java
int nextIndexOf(CharSequence seq) {
    bufferUp();
    final char startChar = seq.charAt(0);
    final int seqLen = seq.length();
    for (int offset = bufPos; offset < bufLength; offset++) {
        if (startChar != charBuf[offset]) {
            while (++offset < bufLength && startChar != charBuf[offset]) { /* empty */ }
        }
        int i = offset + 1;
        int last = i + seqLen - 1;
        if (offset < bufLength && last <= bufLength) {
            for (int j = 1; i < last && seq.charAt(j) == charBuf[i]; i++, j++) { /* empty */ }
            if (i == last)
                return offset - bufPos;
        }
    }
    return -1;
}
```
