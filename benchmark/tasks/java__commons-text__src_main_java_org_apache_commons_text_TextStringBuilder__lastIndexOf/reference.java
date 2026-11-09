public int lastIndexOf(final String str, int startIndex) {
    startIndex = startIndex >= size ? size - 1 : startIndex;
    if (str == null || startIndex < 0) {
        return -1;
    }
    final int strLen = str.length();
    if (strLen > 0 && strLen <= size) {
        if (strLen == 1) {
            return lastIndexOf(str.charAt(0), startIndex);
        }

        outer: for (int i = startIndex - strLen + 1; i >= 0; i--) {
            for (int j = 0; j < strLen; j++) {
                if (str.charAt(j) != buffer[i + j]) {
                    continue outer;
                }
            }
            return i;
        }

    } else if (strLen == 0) {
        return startIndex;
    }
    return -1;
}
