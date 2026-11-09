```java
private static boolean looksLikeUtf8(byte[] input) {
    final int len = input.length;
    int i = 0;
    if (len >= 3 && (input[0] & 0xFF) == 0xEF && (input[1] & 0xFF) == 0xBB && (input[2] & 0xFF) == 0xBF) {
        i = 3;
    }
    for (; i < len; i++) {
        final int o = input[i] & 0xFF;
        if (o < 0x80) continue;
        final int end;
        if ((o & 0xE0) == 0xC0) end = i + 1;
        else if ((o & 0xF0) == 0xE0) end = i + 2;
        else if ((o & 0xF8) == 0xF0) end = i + 3;
        else return false;
        if (end >= len) return false;
        while (i < end) {
            i++;
            if ((input[i] & 0xC0) != 0x80) return false;
        }
    }
    return true;
}
```
