```java
private static String replaceEach(
        final String text, final String[] searchList, final String[] replacementList, final boolean repeat, final int timeToLive) {
    if (text == null || text.isEmpty() || searchList == null || searchList.length == 0
            || replacementList == null || replacementList.length == 0) {
        return text;
    }
    if (timeToLive < 0) {
        throw new IllegalStateException("Aborting to protect against StackOverflowError - output of one loop is the input of another");
    }
    final int n = searchList.length;
    if (n != replacementList.length) {
        throw new IllegalArgumentException("Search and Replace array lengths don't match: " + n + " vs " + replacementList.length);
    }
    // next[i] = index of next occurrence of searchList[i] at or after the current position, -1 if none/ignored
    final int[] next = new int[n];
    boolean any = false;
    for (int i = 0; i < n; i++) {
        final String search = searchList[i];
        if (search == null || search.isEmpty() || replacementList[i] == null) {
            next[i] = -1;
        } else {
            next[i] = text.indexOf(search);
            if (next[i] >= 0) {
                any = true;
            }
        }
    }
    if (!any) {
        return text;
    }
    final StringBuilder buf = new StringBuilder(text.length() + 16);
    int pos = 0;
    while (true) {
        int best = -1;
        int bestIdx = -1;
        for (int i = 0; i < n; i++) {
            if (next[i] >= 0 && (best < 0 || next[i] < best)) {
                best = next[i];
                bestIdx = i;
            }
        }
        if (bestIdx < 0) {
            break;
        }
        buf.append(text, pos, best).append(replacementList[bestIdx]);
        pos = best + searchList[bestIdx].length();
        for (int i = 0; i < n; i++) {
            if (next[i] >= 0 && next[i] < pos) {
                next[i] = text.indexOf(searchList[i], pos);
            }
        }
    }
    buf.append(text, pos, text.length());
    final String result = buf.toString();
    if (!repeat) {
        return result;
    }
    return replaceEach(result, searchList, replacementList, repeat, timeToLive - 1);
}
```
