```java
private static String cacheString(final char[] charBuf, final String[] stringCache, final int start, final int count) {
    if (count > maxStringCacheLen)
        return new String(charBuf, start, count);
    if (count < 1)
        return "";

    int hash = 0;
    int offset = start;
    for (int i = 0; i < count; i++) {
        hash = 31 * hash + charBuf[offset++];
    }

    final int index = hash & (stringCache.length - 1);
    String cached = stringCache[index];

    if (cached != null && rangeEquals(charBuf, start, count, cached))
        return cached;
    cached = new String(charBuf, start, count);
    stringCache[index] = cached;
    return cached;
}
```
