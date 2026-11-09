```java
public static String wrap(final String str, int wrapLength, String newLineStr, final boolean wrapLongWords, String wrapOn) {
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
    final Matcher matcher = patternToWrapOn.matcher(str);
    while (offset < inputLineLength) {
        int spaceToWrapAt = -1;
        final int windowEnd = (int) Math.min((long) inputLineLength, (long) offset + wrapLength + 1L);
        matcher.region(offset, windowEnd);
        if (matcher.find()) {
            if (matcher.start() == offset) {
                offset = matcher.end() > offset ? matcher.end() : offset + 1;
                continue;
            }
            spaceToWrapAt = matcher.start();
        }
        if (inputLineLength - offset <= wrapLength) {
            break;
        }
        while (matcher.find()) {
            spaceToWrapAt = matcher.start();
        }
        if (spaceToWrapAt >= offset) {
            wrappedLine.append(str, offset, spaceToWrapAt);
            wrappedLine.append(newLineStr);
            offset = spaceToWrapAt + 1;
        } else if (wrapLongWords) {
            wrappedLine.append(str, offset, wrapLength + offset);
            wrappedLine.append(newLineStr);
            offset += wrapLength;
        } else {
            matcher.region(offset + wrapLength, inputLineLength);
            if (matcher.find()) {
                spaceToWrapAt = matcher.start();
                wrappedLine.append(str, offset, spaceToWrapAt);
                wrappedLine.append(newLineStr);
                offset = spaceToWrapAt + 1;
            } else {
                wrappedLine.append(str, offset, inputLineLength);
                offset = inputLineLength;
            }
        }
    }
    wrappedLine.append(str, offset, inputLineLength);
    return wrappedLine.toString();
}
```
