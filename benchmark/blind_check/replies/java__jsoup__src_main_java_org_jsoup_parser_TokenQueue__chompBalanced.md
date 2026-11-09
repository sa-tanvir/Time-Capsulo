```java
public String chompBalanced(char open, char close) {
    int start = -1;
    int end = -1;
    int depth = 0;
    char last = 0;
    boolean inSingleQuote = false;
    boolean inDoubleQuote = false;

    do {
        if (isEmpty()) break;
        final char c = consume();
        if (last == 0 || last != ESC) {
            if (c == '\'' && c != open && !inDoubleQuote)
                inSingleQuote = !inSingleQuote;
            else if (c == '"' && c != open && !inSingleQuote)
                inDoubleQuote = !inDoubleQuote;
            if (inSingleQuote || inDoubleQuote)
                continue;

            if (c == open) {
                depth++;
                if (start == -1)
                    start = pos;
            } else if (c == close) {
                depth--;
            }
        }

        if (depth > 0 && last != 0)
            end = pos;
        last = c;
    } while (depth > 0);

    final String out = (end >= 0) ? queue.substring(start, end) : "";
    if (depth > 0) {
        Validate.fail("Did not find balanced marker at '" + out + "'");
    }
    return out;
}
```
