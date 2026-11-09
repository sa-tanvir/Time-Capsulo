You are an expert Java developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Java code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```java code block, with no explanation.

=== SPECIFICATION ===
# Functional specification

## 1. Component overview

`TokenQueue.chompBalanced(open, close)` consumes a balanced, possibly nested, bracketed group from the front of the queue and returns its contents without the outermost open/close pair. jsoup uses it to read selector arguments such as `:contains(one (two) three)`.

## 2. Functional requirements

Characters are consumed one at a time from the current position (advancing the queue's position). Let `c` be the character just consumed and `prev` the character consumed before it as recorded below. The first character consumed is always processed with no `prev`.

1. **Escapes.** If `prev` is a backslash `\`, `c` is taken literally: it neither opens nor closes a group and does not toggle quote state. (`prev` is simply the previous processed character, so in `\\(` the `(` is still treated as escaped; backslashes do not cancel each other.)
2. **Quotes.** Otherwise a single quote `'` toggles "inside single quotes" unless `c` equals `open` or the scan is inside double quotes; a double quote `"` toggles "inside double quotes" unless `c` equals `open` or the scan is inside single quotes. If after this the scan is inside either kind of quotes, `c` is consumed but completely ignored: it does not count for depth, does not become `prev`, and does not extend the captured text (so the opening quote and everything up to, but not including, the closing quote are skipped; the closing quote itself is then processed as an ordinary character).
3. **Depth.** Otherwise a character equal to `open` increases the depth by one (the first time, the capture start is set to just after that character); a character equal to `close` decreases it by one. Depth starts at 0 and may go negative.
4. **Capture end.** After processing any character that was not ignored by rule 2 (including escaped characters), if the depth is greater than 0 and this was not the very first character consumed, the capture end moves to just after `c`; then `c` becomes `prev`. Thus the closing character that brings the depth to 0 is not part of the capture.
5. The scan stops when the queue is empty, or as soon as, after processing a character, the depth is not greater than 0. (So if the first character is not `open`, exactly that one character is consumed and the result is empty.)
6. **Result.** The text from the capture start up to the capture end (the content between the outermost pair, inner brackets, quotes and backslashes unchanged), or the empty string if nothing was captured.
7. **Unbalanced input.** If the scan stopped because the queue was empty while the depth is still greater than 0, throw `IllegalArgumentException` (via the project's validation helper) with the message `Did not find balanced marker at '` + the text that would have been returned + `'`. The consumed characters stay consumed.

## 3. Input specification

`open`, `close`: two distinct `char`s (for example `(` `)`, `[` `]`, `{` `}`, `<` `>`). The queue may hold any text, any length (up to about 100,000 characters), with arbitrary nesting depth.

## 4. Output specification

The captured `String`, with the queue positioned just after the closing character. Examples with `chompBalanced('(', ')')`:
- queue `(one (two) three) four` returns `one (two) three`, remainder ` four`.
- `(one (two) \( \) \) three) four` returns `one (two) \( \) \) three`.
- `(a 'b)' c) d` returns `a 'b)' c`; `(a "b)" c) d` returns `a "b)" c`.
- `unbalanced(x)`: the first character `u` is not `(`, so the result is `""` after consuming just `u`.
- `((a)` throws with message `Did not find balanced marker at '(a)'`.
- `('a) b` throws with message `Did not find balanced marker at ''` (the unterminated quoted part is not captured).
- `(` throws with message `Did not find balanced marker at ''`.

## 5. Edge cases and constraints

- Linear time in the number of characters consumed.
- For an empty queue the result is `""` and no exception is thrown (the depth never became positive).

=== CONTEXT ===
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

=== STUB ===
```java
public String chompBalanced(char open, char close) {
    // TODO: implement according to the specification
}
```
