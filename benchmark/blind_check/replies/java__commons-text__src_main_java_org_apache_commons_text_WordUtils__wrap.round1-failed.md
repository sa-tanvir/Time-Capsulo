```java
public static String wrap(final String str,
                          int wrapLength,
                          String newLineStr,
                          final boolean wrapLongWords,
                          String wrapOn) {
    if (str == null) {
        return null;
    }
    if (newLineStr == null) {
        newLineStr = System.lineSeparator();
    }
    if (wrapLength < 1) {
        wrapLength = 1;
    }
    if (StringUtils.isBlank(wrapOn)) {
        wrapOn = " ";
    }
    final Pattern patternToWrapOn = Pattern.compile(wrapOn);
    final int inputLineLength = str.length();
    int offset = 0;
    final StringBuilder wrappedLine = new StringBuilder(inputLineLength + 32);
    int matcherSize = -1;
    while (offset < inputLineLength) {
        int spaceToWrapAt = -1;
        Matcher matcher = patternToWrapOn.matcher(
            str.substring(offset, (int) Math.min(Integer.MAX_VALUE, Math.min((long) inputLineLength, offset + (long) wrapLength + 1L))));
        if (matcher.find()) {
            if (matcher.start() == 0) {
                matcherSize = matcher.end();
                if (matcherSize != 0) {
                    offset += matcher.end();
                    continue;
                }
                offset += 1;
            }
            spaceToWrapAt = matcher.start() + offset;
        }
        // only last line without leading separators is left
        if (inputLineLength - offset <= wrapLength) {
            break;
        }
        while (matcher.find()) {
            spaceToWrapAt = matcher.start() + offset;
        }
        if (spaceToWrapAt >= offset) {
            // normal case
            wrappedLine.append(str, offset, spaceToWrapAt);
            wrappedLine.append(newLineStr);
            offset = spaceToWrapAt + 1;
        } else if (wrapLongWords) {
            if (matcherSize == 0) {
                offset--;
            }
            // wrap really long word one line at a time
            wrappedLine.append(str, offset, wrapLength + offset);
            wrappedLine.append(newLineStr);
            offset += wrapLength;
            matcherSize = -1;
        } else {
            // do not wrap really long word, just extend beyond limit
            matcher = patternToWrapOn.matcher(str.substring(offset + wrapLength));
            if (matcher.find()) {
                matcherSize = matcher.end() - matcher.start();
                spaceToWrapAt = matcher.start() + offset + wrapLength;
            }
            if (spaceToWrapAt >= 0) {
                if (matcherSize == 0 && offset != 0) {
                    offset--;
                }
                wrappedLine.append(str, offset, spaceToWrapAt);
                wrappedLine.append(newLineStr);
                offset = spaceToWrapAt + 1;
            } else {
                wrappedLine.append(str, offset, str.length());
                offset = inputLineLength;
            }
        }
    }
    if (matcherSize == 0 && offset < inputLineLength) {
        offset--;
    }
    // Whatever is left in line is short enough to just pass through
    wrappedLine.append(str, offset, str.length());
    return wrappedLine.toString();
}
```
