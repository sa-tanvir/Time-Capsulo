```java
public String nysiis(String str) {
    if (str == null) {
        return null;
    }
    str = SoundexUtils.clean(str);
    if (str.length() == 0) {
        return str;
    }
    if (str.startsWith("MAC")) {
        str = "MCC" + str.substring(3);
    }
    if (str.startsWith("KN")) {
        str = "NN" + str.substring(2);
    }
    if (str.startsWith("K")) {
        str = "C" + str.substring(1);
    }
    if (str.startsWith("PH") || str.startsWith("PF")) {
        str = "FF" + str.substring(2);
    }
    if (str.startsWith("SCH")) {
        str = "SSS" + str.substring(3);
    }
    if (str.endsWith("EE") || str.endsWith("IE")) {
        str = str.substring(0, str.length() - 2) + "Y";
    }
    if (str.endsWith("DT") || str.endsWith("RT") || str.endsWith("RD")
            || str.endsWith("NT") || str.endsWith("ND")) {
        str = str.substring(0, str.length() - 2) + "D";
    }

    final char[] chars = str.toCharArray();
    final int len = chars.length;
    final StringBuilder key = new StringBuilder(len);
    key.append(chars[0]);
    for (int i = 1; i < len; i++) {
        final char prev = chars[i - 1];
        final char curr = chars[i];
        final char next = i < len - 1 ? chars[i + 1] : ' ';
        final char aNext = i < len - 2 ? chars[i + 2] : ' ';
        final char[] transcoded = transcodeRemaining(prev, curr, next, aNext);
        System.arraycopy(transcoded, 0, chars, i, transcoded.length);
        if (chars[i] != prev) {
            key.append(chars[i]);
        }
    }

    if (key.length() > 1) {
        char lastChar = key.charAt(key.length() - 1);
        if (lastChar == 'S') {
            key.deleteCharAt(key.length() - 1);
            lastChar = key.charAt(key.length() - 1);
        }
        if (key.length() > 2) {
            final char last2 = key.charAt(key.length() - 2);
            if (last2 == 'A' && lastChar == 'Y') {
                key.deleteCharAt(key.length() - 2);
            }
        }
        if (lastChar == 'A') {
            key.deleteCharAt(key.length() - 1);
        }
    }

    final String result = key.toString();
    return isStrict() ? result.substring(0, Math.min(6, result.length())) : result;
}
```
