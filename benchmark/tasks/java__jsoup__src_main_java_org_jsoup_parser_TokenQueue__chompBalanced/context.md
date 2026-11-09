# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/jsoup/parser/TokenQueue.java`
- **Enclosing scope:** `public class TokenQueue`

## Imports / includes available in this file

```
import org.jsoup.internal.StringUtil;
import org.jsoup.helper.Validate;
```

## Other functions defined in the same file (signatures only; you may call them)

```
TokenQueue::TokenQueue( String data)
TokenQueue::addFirst( Character c)
TokenQueue::addFirst( String seq)
TokenQueue::advance()
TokenQueue::chompTo( String seq)
TokenQueue::chompToIgnoreCase( String seq)
TokenQueue::consume( String seq)
TokenQueue::consume()
TokenQueue::consumeAttributeKey()
TokenQueue::consumeCssIdentifier()
TokenQueue::consumeElementSelector()
TokenQueue::consumeTagName()
TokenQueue::consumeTo( String seq)
TokenQueue::consumeToAny( String ... seq)
TokenQueue::consumeToIgnoreCase( String seq)
TokenQueue::consumeWhitespace()
TokenQueue::consumeWord()
TokenQueue::isEmpty()
TokenQueue::matchChomp( String seq)
TokenQueue::matches( String seq)
TokenQueue::matchesAny( String ... seq)
TokenQueue::matchesAny( char ... seq)
TokenQueue::matchesCS( String seq)
TokenQueue::matchesStartTag()
TokenQueue::matchesWhitespace()
TokenQueue::matchesWord()
TokenQueue::peek()
TokenQueue::remainder()
TokenQueue::remainingLength()
TokenQueue::toString()
TokenQueue::unescape( String in)
```

## Instance state

Fields of `TokenQueue` used by the method:

- `queue` (`String`, private): the text of the queue.
- `pos` (`int`, private): index into `queue` of the next character to read; characters before it are consumed. Everything from `pos` on is "remaining".
- `ESC` (`private static final char`) is the backslash `'\\'`.

Sibling methods you may call: `isEmpty()` (true when no characters remain); `consume()` returns the next character (a `char`) and advances `pos`; `remainder()` returns and consumes the rest. `Validate.fail(String message)` (in `org.jsoup.helper.Validate`) throws `IllegalArgumentException(message)`.

`pos` is also what you read to build the returned substring: the result is `queue.substring(start, end)` for the captured positions.
