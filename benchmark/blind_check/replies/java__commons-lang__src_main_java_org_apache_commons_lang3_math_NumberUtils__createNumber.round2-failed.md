```java
public static Number createNumber(final String str) {
    if (str == null) {
        return null;
    }
    if (StringUtils.isBlank(str)) {
        throw new NumberFormatException("A blank string is not a valid number");
    }
    final String[] hexPrefixes = {"0x", "0X", "-0x", "-0X", "#", "-#"};
    int pfxLen = 0;
    for (final String pfx : hexPrefixes) {
        if (str.startsWith(pfx)) {
            pfxLen = pfx.length();
            break;
        }
    }
    if (pfxLen > 0) {
        char firstSigDigit = 0;
        for (int i = pfxLen; i < str.length(); i++) {
            firstSigDigit = str.charAt(i);
            if (firstSigDigit == '0') {
                pfxLen++;
            } else {
                break;
            }
        }
        final int hexDigits = str.length() - pfxLen;
        if (hexDigits > 16 || hexDigits == 16 && firstSigDigit > '7') {
            return createBigInteger(str);
        }
        if (hexDigits > 8 || hexDigits == 8 && firstSigDigit > '7') {
            return createLong(str);
        }
        return createInteger(str);
    }
    final int eLower = str.indexOf('e');
    final int eUpper = str.indexOf('E');
    if (eLower >= 0 && eUpper >= 0) {
        throw new NumberFormatException(str + " is not a valid number.");
    }
    final int expPos = eLower >= 0 ? eLower : eUpper;
    final int decPos = str.indexOf('.');
    if (decPos >= 0 && expPos >= 0 && expPos < decPos) {
        throw new NumberFormatException(str + " is not a valid number.");
    }
    final int len = str.length();
    final char lastChar = str.charAt(len - 1);
    final boolean hasSuffix = !Character.isDigit(lastChar) && lastChar != '.';
    if (hasSuffix) {
        if ("lLfFdD".indexOf(lastChar) < 0) {
            throw new NumberFormatException(str + " is not a valid number.");
        }
        final String numeric = str.substring(0, len - 1);
        final String exp = expPos >= 0 ? str.substring(expPos + 1, len - 1) : null;
        String mant;
        if (decPos >= 0) {
            mant = str.substring(0, decPos);
        } else if (expPos >= 0) {
            mant = str.substring(0, expPos);
        } else {
            mant = str;
        }
        if (!mant.isEmpty() && (mant.charAt(0) == '+' || mant.charAt(0) == '-')) {
            mant = mant.substring(1);
        }
        final boolean allZeros = isAllZeros(mant) && isAllZeros(exp);
        switch (lastChar) {
        case 'l':
        case 'L':
            if (decPos < 0 && expPos < 0
                    && (isDigits(numeric) || numeric.charAt(0) == '-' && isDigits(numeric.substring(1)))) {
                try {
                    return createLong(numeric);
                } catch (final NumberFormatException ignored) {
                    return createBigInteger(numeric);
                }
            }
            throw new NumberFormatException(str + " is not a valid number.");
        case 'f':
        case 'F':
            try {
                final Float f = createFloat(str);
                if (!f.isInfinite() && !(f.floatValue() == 0.0F && !allZeros)) {
                    return f;
                }
            } catch (final NumberFormatException ignored) {
                // fall through to double
            }
            // fall through
        case 'd':
        case 'D':
            try {
                final Double d = createDouble(str);
                if (!d.isInfinite() && !(d.floatValue() == 0.0F && !allZeros)) {
                    return d;
                }
            } catch (final NumberFormatException ignored) {
                // ignore
            }
            try {
                return createBigDecimal(numeric);
            } catch (final NumberFormatException ignored) {
                // ignore
            }
            break;
        default:
            break;
        }
        throw new NumberFormatException(str + " is not a valid number.");
    }
    if (decPos < 0 && expPos < 0) {
        try {
            return createInteger(str);
        } catch (final NumberFormatException ignored) {
            // ignore
        }
        try {
            return createLong(str);
        } catch (final NumberFormatException ignored) {
            // ignore
        }
        return createBigInteger(str);
    }
    String mant;
    if (decPos >= 0) {
        mant = str.substring(0, decPos);
    } else {
        mant = str.substring(0, expPos);
    }
    if (!mant.isEmpty() && (mant.charAt(0) == '+' || mant.charAt(0) == '-')) {
        mant = mant.substring(1);
    }
    final String exp = expPos >= 0 ? str.substring(expPos + 1) : null;
    final boolean allZeros = isAllZeros(mant) && isAllZeros(exp);
    try {
        final Float f = createFloat(str);
        final Double d = createDouble(str);
        if (!f.isInfinite() && !(f.floatValue() == 0.0F && !allZeros) && f.toString().equals(d.toString())) {
            return f;
        }
        if (!d.isInfinite() && !(d.doubleValue() == 0.0D && !allZeros)) {
            final BigDecimal b = createBigDecimal(str);
            if (b.compareTo(BigDecimal.valueOf(d.doubleValue())) == 0) {
                return d;
            }
            return b;
        }
    } catch (final NumberFormatException ignored) {
        // ignore
    }
    return createBigDecimal(str);
}
```
