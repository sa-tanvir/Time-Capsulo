```java
public int translate(final CharSequence input, final int index, final Writer out) throws IOException {
    final int seqEnd = input.length();
    if (input.charAt(index) == '&' && index < seqEnd - 2 && input.charAt(index + 1) == '#') {
        int start = index + 2;
        boolean isHex = false;
        final char firstChar = input.charAt(start);
        if (firstChar == 'x' || firstChar == 'X') {
            start++;
            isHex = true;
            if (start == seqEnd) {
                return 0;
            }
        }
        int end = start;
        while (end < seqEnd) {
            final char c = input.charAt(end);
            if (c >= '0' && c <= '9' || c >= 'a' && c <= 'f' || c >= 'A' && c <= 'F') {
                end++;
            } else {
                break;
            }
        }
        final boolean semiNext = end != seqEnd && input.charAt(end) == ';';
        if (!semiNext) {
            if (isSet(OPTION.semiColonRequired)) {
                return 0;
            }
            if (isSet(OPTION.errorIfNoSemiColon)) {
                throw new IllegalArgumentException("Semi-colon required at end of numeric entity");
            }
        }
        final int entityValue;
        try {
            final String digits = input.subSequence(start, end).toString();
            entityValue = Integer.parseInt(digits, isHex ? 16 : 10);
        } catch (final NumberFormatException nfe) {
            return 0;
        }
        if (entityValue > 0xFFFF) {
            final char[] chrs = Character.toChars(entityValue);
            out.write(chrs[0]);
            out.write(chrs[1]);
        } else {
            out.write(entityValue);
        }
        return 2 + end - start + (isHex ? 1 : 0) + (semiNext ? 1 : 0);
    }
    return 0;
}
```
