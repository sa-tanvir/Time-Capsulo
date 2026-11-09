```java
public String soundex(String str) {
    if (str == null) {
        return null;
    }
    str = SoundexUtils.clean(str);
    if (str.length() == 0) {
        return str;
    }
    final char[] out = {'0', '0', '0', '0'};
    int count = 0;
    final char first = str.charAt(0);
    out[count++] = first;
    char last = map(first);
    for (int i = 1; i < str.length() && count < out.length; i++) {
        final char ch = str.charAt(i);
        if (specialCaseHW && (ch == 'H' || ch == 'W')) {
            continue;
        }
        final char mapped = map(ch);
        if (mapped == SILENT_MARKER) {
            continue;
        }
        if (mapped != '0' && mapped != last) {
            out[count++] = mapped;
        }
        last = mapped;
    }
    return new String(out);
}
```
