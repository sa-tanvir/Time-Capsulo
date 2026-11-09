public String colognePhonetic(final String text) {
    if (text == null) {
        return null;
    }

    final CologneInputBuffer input = new CologneInputBuffer(preprocess(text));
    final CologneOutputBuffer output = new CologneOutputBuffer(input.length() * 2);

    char nextChar;

    char lastChar = CHAR_IGNORE;
    char chr;

    while (input.length() > 0) {
        chr = input.removeNext();

        if (input.length() > 0) {
            nextChar = input.getNextChar();
        } else {
            nextChar = CHAR_IGNORE;
        }

        if (chr < 'A' || chr > 'Z') {
                continue; // ignore unwanted characters
        }

        if (arrayContains(AEIJOUY, chr)) {
            output.put('0');
        } else if (chr == 'B' || (chr == 'P' && nextChar != 'H')) {
            output.put('1');
        } else if ((chr == 'D' || chr == 'T') && !arrayContains(CSZ, nextChar)) {
            output.put('2');
        } else if (arrayContains(FPVW, chr)) {
            output.put('3');
        } else if (arrayContains(GKQ, chr)) {
            output.put('4');
        } else if (chr == 'X' && !arrayContains(CKQ, lastChar)) {
            output.put('4');
            output.put('8');
        } else if (chr == 'S' || chr == 'Z') {
            output.put('8');
        } else if (chr == 'C') {
            if (output.length() == 0) {
                if (arrayContains(AHKLOQRUX, nextChar)) {
                    output.put('4');
                } else {
                    output.put('8');
                }
            } else {
                if (arrayContains(SZ, lastChar) || !arrayContains(AHKOQUX, nextChar)) {
                    output.put('8');
                } else {
                    output.put('4');
                }
            }
        } else if (arrayContains(DTX, chr)) {
            output.put('8');
        } else if (chr == 'R') {
            output.put('7');
        } else if (chr == 'L') {
            output.put('5');
        } else if (chr == 'M' || chr == 'N') {
            output.put('6');
        } else if (chr == 'H') {
            output.put(CHAR_IGNORE); // needed by put
        } else {
            // ignored; should not happen
        }

        lastChar = chr;
    }
    return output.toString();
}
