```java
private static String[] splitWorker(final String str, final String separatorChars, final int max, final boolean preserveAllTokens) {
    if (str == null) {
        return null;
    }
    final int len = str.length();
    if (len == 0) {
        return ArrayUtils.EMPTY_STRING_ARRAY;
    }
    final List<String> list = new ArrayList<>();
    int sizePlus1 = 1;
    int i = 0;
    int start = 0;
    boolean match = false;
    boolean lastMatch = false;
    while (i < len) {
        final char c = str.charAt(i);
        final boolean isSep = separatorChars == null ? Character.isWhitespace(c) : separatorChars.indexOf(c) >= 0;
        if (isSep) {
            if (match || preserveAllTokens) {
                lastMatch = true;
                if (sizePlus1++ == max) {
                    i = len;
                    lastMatch = false;
                }
                list.add(str.substring(start, i));
                match = false;
            }
            start = ++i;
            continue;
        }
        lastMatch = false;
        match = true;
        i++;
    }
    if (match || preserveAllTokens && lastMatch) {
        list.add(str.substring(start, i));
    }
    return list.toArray(ArrayUtils.EMPTY_STRING_ARRAY);
}
```
