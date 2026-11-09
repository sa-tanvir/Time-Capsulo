```java
public static Number createNumber(final String str) {
    if (str == null) {
        return null;
    }
    if (StringUtils.isBlank(str)) {
        throw new NumberFormatException("A blank string is not a valid number");
    }
    final int len = str.length();
    final int signLen = str.charAt(0) == '-' ? 1 : 0;
    int pfxEnd = -1;
    if (str.startsWith("0x", signLen) || str.startsWith("0X", signLen)) {
        pfxEnd = signLen + 2;
    } else if (str.startsWith("#", signLen)) {
        pfxEnd = signLen + 1;
    }
    if (pfxEnd >= 0) {
        int idx = pfxEnd;
        while (idx < len && str.charAt(idx) == '0') {
            idx++;
        }
        final int h = len - idx;
        final char c = h > 0 ? str.charAt(idx) : '0';
        if (h > 16 || h == 16 && c > '7') {
            return createBigInteger(str);
        }
        if (h > 8 || h == 8 && c > '7') {
            return createLong(str);
        }
        return createInteger(str);
    }
    final int ePos = str.indexOf('e');
    final int EPos = str.indexOf('E');
    if (ePos >= 0 && EPos >= 0) {
        throw new NumberFormatException(str + " is not a valid number.");
    }
    final int expPos = ePos >= 0 ? ePos : EPos;
    final int dotPos = str.indexOf('.');
    if (dotPos >= 0 && expPos >= 0 && expPos < dotPos) {
        throw new NumberFormatException(str + " is not a valid number.");
    }
    final char last = str.charAt(len - 1);
    final boolean suffixed = !Character.isDigit(last) && last != '.';
    if (suffixed) {
        switch (last) {
        case 'l': case 'L': case 'f': case 'F': case 'd': case 'D':
            break;
        default:
            throw new NumberFormatException(str + " is not a valid number.");
        }
    }
    final int end = suffixed ? len - 1 : len;
    final String numeric = str.substring(0, end);
    final char first = str.charAt(0);
    final int start = first == '+' || first == '-' ? 1 : 0;
    final String mantissa;
    if (dotPos >= 0) {
        mantissa = str.substring(start, dotPos);
    } else if (expPos >= 0) {
        mantissa = str.substring(start, expPos);
    } else {
        mantissa = str.substring(start);
    }
    boolean allZeros = !mantissa.isEmpty() && isAllZeros(mantissa);
    if (allZeros && expPos >= 0) {
        final String exponent = str.substring(expPos + 1, end);
        allZeros = !exponent.isEmpty() && isAllZeros(exponent);
    }
    if (suffixed) {
        switch (last) {
        case 'l':
        case 'L': {
            if (dotPos < 0 && expPos < 0) {
                final String digits = numeric.startsWith("-") ? numeric.substring(1) : numeric;
                if (isDigits(digits)) {
                    try {
                        return createLong(numeric);
                    } catch (final NumberFormatException ignored) {
                        return createBigInteger(numeric);
                    }
                }
            }
            throw new NumberFormatException(str + " is not a valid number.");
        }
        case 'f':
        case 'F':
            try {
                final Float f = createFloat(str);
                if (!(f.isInfinite() || f.floatValue() == 0.0F && !allZeros)) {
                    return f;
                }
            } catch (final NumberFormatException ignored) {
                // fall through to double
            }
            // fall through
        default:
            try {
                final Double d = createDouble(str);
                if (!(d.isInfinite() || d.floatValue() == 0.0F && !allZeros)) {
                    return d;
                }
            } catch (final NumberFormatException ignored) {
                // try BigDecimal
            }
            try {
                return createBigDecimal(numeric);
            } catch (final NumberFormatException ignored) {
                // fall through
            }
            throw new NumberFormatException(str + " is not a valid number.");
        }
    }
    if (dotPos < 0 && expPos < 0) {
        try {
            return createInteger(str);
        } catch (final NumberFormatException ignored) {
            // try long
        }
        try {
            return createLong(str);
        } catch (final NumberFormatException ignored) {
            // try BigInteger
        }
        return createBigInteger(str);
    }
    try {
        final Float f = createFloat(str);
        final Double d = createDouble(str);
        if (!f.isInfinite() && !(f.floatValue() == 0.0F && !allZeros) && f.toString().equals(d.toString())) {
            return f;
        }
        if (!d.isInfinite() && !(d.doubleValue() == 0.0D && !allZeros)) {
            final BigDecimal b = createBigDecimal(str);
            if (b.compareTo(BigDecimal.valueOf(d)) == 0) {
                return d;
            }
            return b;
        }
    } catch (final NumberFormatException ignored) {
        // fall through
    }
    return createBigDecimal(str);
}
```
