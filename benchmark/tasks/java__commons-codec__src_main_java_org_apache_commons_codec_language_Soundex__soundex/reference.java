public String soundex(String str) {
    if (str == null) {
        return null;
    }
    str = SoundexUtils.clean(str);
    if (str.length() == 0) {
        return str;
    }
    final char out[] = {'0', '0', '0', '0'};
    int count = 0;
    final char first = str.charAt(0);
    out[count++] = first;
    char lastDigit = map(first); // previous digit
    for(int i = 1; i < str.length() && count < out.length ; i++) {
        final char ch = str.charAt(i);
        if ((this.specialCaseHW) && (ch == 'H' || ch == 'W')) { // these are ignored completely
            continue;
        }
        final char digit = map(ch);
        if (digit == SILENT_MARKER) {
            continue;
        }
        if (digit != '0' && digit != lastDigit) { // don't store vowels or repeats
            out[count++] = digit;
        }
        lastDigit = digit;
    }
    return new String(out);
}
