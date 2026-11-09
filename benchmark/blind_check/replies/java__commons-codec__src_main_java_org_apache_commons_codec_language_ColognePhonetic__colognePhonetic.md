```java
public String colognePhonetic(final String text) {
    if (text == null) {
        return null;
    }
    final char[] input = preprocess(text);
    final StringBuilder out = new StringBuilder(input.length);
    char lastCode = '/';
    char last = '\0';
    for (int i = 0; i < input.length; i++) {
        final char chr = input[i];
        if (chr < 'A' || chr > 'Z') {
            continue;
        }
        final char next = i + 1 < input.length ? input[i + 1] : '\0';
        char code = '-';
        char code2 = '-';
        switch (chr) {
        case 'A': case 'E': case 'I': case 'J': case 'O': case 'U': case 'Y':
            code = '0';
            break;
        case 'H':
            break;
        case 'B':
            code = '1';
            break;
        case 'P':
            code = next == 'H' ? '3' : '1';
            break;
        case 'F': case 'V': case 'W':
            code = '3';
            break;
        case 'D': case 'T':
            code = (next == 'C' || next == 'S' || next == 'Z') ? '8' : '2';
            break;
        case 'G': case 'K': case 'Q':
            code = '4';
            break;
        case 'X':
            if (last == 'C' || last == 'K' || last == 'Q') {
                code = '8';
            } else {
                code = '4';
                code2 = '8';
            }
            break;
        case 'S': case 'Z':
            code = '8';
            break;
        case 'C':
            if (out.length() == 0) {
                code = (next == 'A' || next == 'H' || next == 'K' || next == 'L' || next == 'O'
                        || next == 'Q' || next == 'R' || next == 'U' || next == 'X') ? '4' : '8';
            } else if (last == 'S' || last == 'Z') {
                code = '8';
            } else {
                code = (next == 'A' || next == 'H' || next == 'K' || next == 'O'
                        || next == 'Q' || next == 'U' || next == 'X') ? '4' : '8';
            }
            break;
        case 'R':
            code = '7';
            break;
        case 'L':
            code = '5';
            break;
        case 'M': case 'N':
            code = '6';
            break;
        default:
            break;
        }
        if (code != '-' && code != lastCode && (code != '0' || out.length() == 0)) {
            out.append(code);
        }
        lastCode = code;
        if (code2 != '-') {
            if (code2 != lastCode) {
                out.append(code2);
            }
            lastCode = code2;
        }
        last = chr;
    }
    return out.toString();
}
```
