```java
public static boolean isCreatable(final String str) {
    if (StringUtils.isEmpty(str)) {
        return false;
    }
    final int total = str.length();
    final int start = str.charAt(0) == '-' || str.charAt(0) == '+' ? 1 : 0;
    if (total > start + 1 && str.charAt(start) == '0' && str.indexOf('.') < 0) {
        final char second = str.charAt(start + 1);
        if (second == 'x' || second == 'X') {
            int i = start + 2;
            if (i == total) {
                return false;
            }
            for (; i < total; i++) {
                final char c = str.charAt(i);
                if (!(c >= '0' && c <= '9' || c >= 'a' && c <= 'f' || c >= 'A' && c <= 'F')) {
                    return false;
                }
            }
            return true;
        }
        if (second >= '0' && second <= '9') {
            for (int i = start + 1; i < total; i++) {
                final char c = str.charAt(i);
                if (c < '0' || c > '7') {
                    return false;
                }
            }
            return true;
        }
    }
    boolean hasExp = false;
    boolean hasDecPoint = false;
    boolean allowSigns = false;
    boolean foundDigit = false;
    final int sz = total - 1;
    int i = start;
    while (i < sz || i < sz + 1 && allowSigns && !foundDigit) {
        final char c = str.charAt(i);
        if (c >= '0' && c <= '9') {
            foundDigit = true;
            allowSigns = false;
        } else if (c == '.') {
            if (hasDecPoint || hasExp) {
                return false;
            }
            hasDecPoint = true;
        } else if (c == 'e' || c == 'E') {
            if (hasExp || !foundDigit) {
                return false;
            }
            hasExp = true;
            allowSigns = true;
        } else if (c == '+' || c == '-') {
            if (!allowSigns) {
                return false;
            }
            allowSigns = false;
            foundDigit = false;
        } else {
            return false;
        }
        i++;
    }
    if (i < total) {
        final char c = str.charAt(i);
        if (c >= '0' && c <= '9') {
            return true;
        }
        if (c == 'e' || c == 'E') {
            return false;
        }
        if (c == '.') {
            if (hasDecPoint || hasExp) {
                return false;
            }
            return foundDigit;
        }
        if (c == 'l' || c == 'L') {
            return !allowSigns && foundDigit && !hasExp && !hasDecPoint;
        }
        if (c == 'd' || c == 'D' || c == 'f' || c == 'F') {
            return !allowSigns && foundDigit;
        }
        return false;
    }
    return !allowSigns && foundDigit;
}
```
