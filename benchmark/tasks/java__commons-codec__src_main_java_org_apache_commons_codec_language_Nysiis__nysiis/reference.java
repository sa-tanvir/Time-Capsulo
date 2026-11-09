public String nysiis(String str) {
    if (str == null) {
        return null;
    }

    // Use the same clean rules as Soundex
    str = SoundexUtils.clean(str);

    if (str.length() == 0) {
        return str;
    }

    // Translate first characters of name:
    // MAC -> MCC, KN -> NN, K -> C, PH | PF -> FF, SCH -> SSS
    str = PAT_MAC.matcher(str).replaceFirst("MCC");
    str = PAT_KN.matcher(str).replaceFirst("NN");
    str = PAT_K.matcher(str).replaceFirst("C");
    str = PAT_PH_PF.matcher(str).replaceFirst("FF");
    str = PAT_SCH.matcher(str).replaceFirst("SSS");

    // Translate last characters of name:
    // EE -> Y, IE -> Y, DT | RT | RD | NT | ND -> D
    str = PAT_EE_IE.matcher(str).replaceFirst("Y");
    str = PAT_DT_ETC.matcher(str).replaceFirst("D");

    // First character of key = first character of name.
    final StringBuilder key = new StringBuilder(str.length());
    key.append(str.charAt(0));

    // Transcode remaining characters, incrementing by one character each time
    final char[] chars = str.toCharArray();
    final int len = chars.length;

    for (int i = 1; i < len; i++) {
        final char next = i < len - 1 ? chars[i + 1] : SPACE;
        final char aNext = i < len - 2 ? chars[i + 2] : SPACE;
        final char[] transcoded = transcodeRemaining(chars[i - 1], chars[i], next, aNext);
        System.arraycopy(transcoded, 0, chars, i, transcoded.length);

        // only append the current char to the key if it is different from the last one
        if (chars[i] != chars[i - 1]) {
            key.append(chars[i]);
        }
    }

    if (key.length() > 1) {
        char lastChar = key.charAt(key.length() - 1);

        // If last character is S, remove it.
        if (lastChar == 'S') {
            key.deleteCharAt(key.length() - 1);
            lastChar = key.charAt(key.length() - 1);
        }

        if (key.length() > 2) {
            final char last2Char = key.charAt(key.length() - 2);
            // If last characters are AY, replace with Y.
            if (last2Char == 'A' && lastChar == 'Y') {
                key.deleteCharAt(key.length() - 2);
            }
        }

        // If last character is A, remove it.
        if (lastChar == 'A') {
            key.deleteCharAt(key.length() - 1);
        }
    }

    final String string = key.toString();
    return this.isStrict() ? string.substring(0, Math.min(TRUE_LENGTH, string.length())) : string;
}
