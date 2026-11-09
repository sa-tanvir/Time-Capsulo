```java
static Token[] lexx(final String format) {
    final ArrayList<Token> list = new ArrayList<>(format.length());
    boolean inLiteral = false;
    StringBuilder buffer = null;
    Token previous = null;
    for (int i = 0; i < format.length(); i++) {
        final char ch = format.charAt(i);
        if (inLiteral && ch != '\'') {
            buffer.append(ch);
            continue;
        }
        Object value = null;
        switch (ch) {
        case '\'':
            if (inLiteral) {
                buffer = null;
                inLiteral = false;
            } else {
                buffer = new StringBuilder();
                list.add(new Token(buffer));
                inLiteral = true;
            }
            break;
        case 'y':
            value = y;
            break;
        case 'M':
            value = M;
            break;
        case 'd':
            value = d;
            break;
        case 'H':
            value = H;
            break;
        case 'm':
            value = m;
            break;
        case 's':
            value = s;
            break;
        case 'S':
            value = S;
            break;
        default:
            if (buffer == null) {
                buffer = new StringBuilder();
                list.add(new Token(buffer));
            }
            buffer.append(ch);
            break;
        }
        if (value != null) {
            if (previous != null && previous.getValue() == value) {
                previous.increment();
            } else {
                final Token token = new Token(value);
                list.add(token);
                previous = token;
            }
            buffer = null;
        }
    }
    if (inLiteral) {
        throw new IllegalArgumentException("Unmatched quote in format: " + format);
    }
    return list.toArray(new Token[0]);
}
```
