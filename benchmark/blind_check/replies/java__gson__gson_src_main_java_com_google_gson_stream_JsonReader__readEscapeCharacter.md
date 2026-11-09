```java
private char readEscapeCharacter() throws IOException {
    if (pos == limit && !fillBuffer(1)) {
        throw syntaxError("Unterminated escape sequence");
    }

    char escaped = buffer[pos++];
    switch (escaped) {
        case 'u':
            if (pos + 4 > limit && !fillBuffer(4)) {
                throw syntaxError("Unterminated escape sequence");
            }
            // Equivalent to Integer.parseInt(stringPool.get(buffer, pos, 4), 16), but without allocating
            char result = 0;
            for (int i = pos, end = i + 4; i < end; i++) {
                char c = buffer[i];
                result <<= 4;
                if (c >= '0' && c <= '9') {
                    result += (c - '0');
                } else if (c >= 'a' && c <= 'f') {
                    result += (c - 'a' + 10);
                } else if (c >= 'A' && c <= 'F') {
                    result += (c - 'A' + 10);
                } else {
                    throw new NumberFormatException("\\u" + new String(buffer, pos, 4));
                }
            }
            pos += 4;
            return result;

        case 't':
            return '\t';

        case 'b':
            return '\b';

        case 'n':
            return '\n';

        case 'r':
            return '\r';

        case 'f':
            return '\f';

        case '\n':
            lineNumber++;
            lineStart = pos;
            // fall-through

        case '\'':
        case '"':
        case '\\':
        case '/':
            return escaped;

        default:
            // throw error when none of the above cases are matched
            throw syntaxError("Invalid escape sequence");
    }
}
```
