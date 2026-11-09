```java
private int readArgumentIndex(final String pattern, final ParsePosition pos) {
    final int start = pos.getIndex();
    seekNonWs(pattern, pos);
    final StringBuilder result = new StringBuilder();
    boolean error = false;
    for (; !error && pos.getIndex() < pattern.length(); next(pos)) {
        char c = pattern.charAt(pos.getIndex());
        if (Character.isWhitespace(c)) {
            seekNonWs(pattern, pos);
            c = pattern.charAt(pos.getIndex());
            if (c != START_FMT && c != END_FE) {
                error = true;
                continue;
            }
        }
        if ((c == START_FMT || c == END_FE) && result.length() > 0) {
            try {
                return Integer.parseInt(result.toString());
            } catch (final NumberFormatException ignored) {
                // out of int range: treat terminator as invalid below
            }
        }
        error = !Character.isDigit(c);
        result.append(c);
    }
    if (error) {
        throw new IllegalArgumentException(
            "Invalid format argument index at position " + start + ": "
                + pattern.substring(start, pos.getIndex()));
    }
    throw new IllegalArgumentException("Unterminated format element at position " + start);
}
```
