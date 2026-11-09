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
    int pos = 0;
    int emptyFlag = -1;
    final StringBuilder sb = new StringBuilder(inputLineLength + 32);
    while (pos < inputLineLength) {
        final int end = (int) Math.min((long) inputLineLength, (long) pos + wrapLength + 1);
        final Matcher matcher = patternToWrapOn.matcher(str.substring(pos, end));
        int cand = -1;
        if (matcher.find()) {
            if (matcher.start() == 0) {
                emptyFlag = matcher.end() - matcher.start();
                if (emptyFlag != 0) {
                    pos += emptyFlag;
                    continue;
                }
                pos += 1;
            }
            cand = pos + matcher.start();
        }
        if (inputLineLength - pos <= wrapLength) {
            break;
        }
        while (matcher.find()) {
            cand = pos + matcher.start();
        }
        if (cand >= pos) {
            sb.append(str, pos, cand).append(newLineStr);
            pos = cand + 1;
        } else if (wrapLongWords) {
            if (emptyFlag == 0) {
                pos--;
            }
            sb.append(str, pos, pos + wrapLength).append(newLineStr);
            pos += wrapLength;
            emptyFlag = -1;
        } else {
            final Matcher m2 = patternToWrapOn.matcher(str.substring(pos + wrapLength));
            if (m2.find()) {
                emptyFlag = m2.end() - m2.start();
                cand = pos + wrapLength + m2.start();
            }
            if (cand >= 0) {
                if (emptyFlag == 0 && pos != 0) {
                    pos--;
                }
                sb.append(str, pos, cand).append(newLineStr);
                pos = cand + 1;
            } else {
                if (emptyFlag == 0 && pos != 0) {
                    pos--;
                }
                sb.append(str, pos, inputLineLength);
                pos = inputLineLength;
                emptyFlag = -1;
            }
        }
    }
    if (emptyFlag == 0 && pos < inputLineLength) {
        pos--;
    }
    sb.append(str, pos, inputLineLength);
    return sb.toString();
}
```
