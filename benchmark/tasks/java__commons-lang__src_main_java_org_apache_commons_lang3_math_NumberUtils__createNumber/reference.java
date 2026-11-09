public static Number createNumber(final String str) {
    if (str == null) {
        return null;
    }
    if (StringUtils.isBlank(str)) {
        throw new NumberFormatException("A blank string is not a valid number");
    }
    // Need to deal with all possible hex prefixes here
    final String[] hex_prefixes = {"0x", "0X", "-0x", "-0X", "#", "-#"};
    int pfxLen = 0;
    for (final String pfx : hex_prefixes) {
        if (str.startsWith(pfx)) {
            pfxLen += pfx.length();
            break;
        }
    }
    if (pfxLen > 0) { // we have a hex number
        char firstSigDigit = 0; // strip leading zeroes
        for (int i = pfxLen; i < str.length(); i++) {
            firstSigDigit = str.charAt(i);
            if (firstSigDigit == '0') { // count leading zeroes
                pfxLen++;
            } else {
                break;
            }
        }
        final int hexDigits = str.length() - pfxLen;
        if (hexDigits > 16 || hexDigits == 16 && firstSigDigit > '7') { // too many for Long
            return createBigInteger(str);
        }
        if (hexDigits > 8 || hexDigits == 8 && firstSigDigit > '7') { // too many for an int
            return createLong(str);
        }
        return createInteger(str);
    }
    final char lastChar = str.charAt(str.length() - 1);
    String mant;
    String dec;
    String exp;
    final int decPos = str.indexOf('.');
    final int expPos = str.indexOf('e') + str.indexOf('E') + 1; // assumes both not present
    // if both e and E are present, this is caught by the checks on expPos (which prevent IOOBE)
    // and the parsing which will detect if e or E appear in a number due to using the wrong offset

    if (decPos > -1) { // there is a decimal point
        if (expPos > -1) { // there is an exponent
            if (expPos < decPos || expPos > str.length()) { // prevents double exponent causing IOOBE
                throw new NumberFormatException(str + " is not a valid number.");
            }
            dec = str.substring(decPos + 1, expPos);
        } else {
            dec = str.substring(decPos + 1);
        }
        mant = getMantissa(str, decPos);
    } else {
        if (expPos > -1) {
            if (expPos > str.length()) { // prevents double exponent causing IOOBE
                throw new NumberFormatException(str + " is not a valid number.");
            }
            mant = getMantissa(str, expPos);
        } else {
            mant = getMantissa(str);
        }
        dec = null;
    }
    if (!Character.isDigit(lastChar) && lastChar != '.') {
        if (expPos > -1 && expPos < str.length() - 1) {
            exp = str.substring(expPos + 1, str.length() - 1);
        } else {
            exp = null;
        }
        //Requesting a specific type..
        final String numeric = str.substring(0, str.length() - 1);
        final boolean allZeros = isAllZeros(mant) && isAllZeros(exp);
        switch (lastChar) {
            case 'l' :
            case 'L' :
                if (dec == null
                    && exp == null
                    && (!numeric.isEmpty() && numeric.charAt(0) == '-' && isDigits(numeric.substring(1)) || isDigits(numeric))) {
                    try {
                        return createLong(numeric);
                    } catch (final NumberFormatException nfe) { // NOPMD
                        // Too big for a long
                    }
                    return createBigInteger(numeric);

                }
                throw new NumberFormatException(str + " is not a valid number.");
            case 'f' :
            case 'F' :
                try {
                    final Float f = createFloat(str);
                    if (!(f.isInfinite() || f.floatValue() == 0.0F && !allZeros)) {
                        //If it's too big for a float or the float value = 0 and the string
                        //has non-zeros in it, then float does not have the precision we want
                        return f;
                    }

                } catch (final NumberFormatException nfe) { // NOPMD
                    // ignore the bad number
                }
                //$FALL-THROUGH$
            case 'd' :
            case 'D' :
                try {
                    final Double d = createDouble(str);
                    if (!(d.isInfinite() || d.floatValue() == 0.0D && !allZeros)) {
                        return d;
                    }
                } catch (final NumberFormatException nfe) { // NOPMD
                    // ignore the bad number
                }
                try {
                    return createBigDecimal(numeric);
                } catch (final NumberFormatException e) { // NOPMD
                    // ignore the bad number
                }
                //$FALL-THROUGH$
            default :
                throw new NumberFormatException(str + " is not a valid number.");

        }
    }
    //User doesn't have a preference on the return type, so let's start
    //small and go from there...
    if (expPos > -1 && expPos < str.length() - 1) {
        exp = str.substring(expPos + 1, str.length());
    } else {
        exp = null;
    }
    if (dec == null && exp == null) { // no decimal point and no exponent
        //Must be an Integer, Long, Biginteger
        try {
            return createInteger(str);
        } catch (final NumberFormatException nfe) { // NOPMD
            // ignore the bad number
        }
        try {
            return createLong(str);
        } catch (final NumberFormatException nfe) { // NOPMD
            // ignore the bad number
        }
        return createBigInteger(str);
    }

    //Must be a Float, Double, BigDecimal
    final boolean allZeros = isAllZeros(mant) && isAllZeros(exp);
    try {
        final Float f = createFloat(str);
        final Double d = createDouble(str);
        if (!f.isInfinite()
                && !(f.floatValue() == 0.0F && !allZeros)
                && f.toString().equals(d.toString())) {
            return f;
        }
        if (!d.isInfinite() && !(d.doubleValue() == 0.0D && !allZeros)) {
            final BigDecimal b = createBigDecimal(str);
            if (b.compareTo(BigDecimal.valueOf(d.doubleValue())) == 0) {
                return d;
            }
            return b;
        }
    } catch (final NumberFormatException nfe) { // NOPMD
        // ignore the bad number
    }
    return createBigDecimal(str);
}
