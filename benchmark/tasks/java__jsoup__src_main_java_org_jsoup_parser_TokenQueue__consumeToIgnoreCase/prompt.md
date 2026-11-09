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

`TokenQueue.consumeToIgnoreCase(seq)` consumes characters from the front of the queue up to, but not including, the next position where `seq` occurs (ignoring case), and returns the consumed text. jsoup uses it to find the end of raw-text elements such as `</script` or `</textarea`.

## 2. Functional requirements

Let the queue hold `queue` and let `pos` be the current read position (characters before `pos` have already been consumed).

1. Find the smallest position `p >= pos` such that the characters of the queue starting at `p` match `seq` case-insensitively (as `TokenQueue.matches(String)` does: `String.regionMatches` with `ignoreCase`; a match needs the full length of `seq` to be available). A match at `pos` itself counts.
2. Advance the position to `p` and return the text between the old position and `p`. If the queue is already positioned at a match, return the empty string and do not move.
3. If there is no match anywhere in the remaining text, consume everything: the position moves to the end of the queue and the whole remaining text is returned (empty if the queue was already empty).
4. The matched text itself is not consumed. A later call on the same queue starts from where this one stopped (typically after the caller has consumed the matched sequence; for example `chompToIgnoreCase` consumes `seq` afterwards, so two successive calls with the same `seq` return the text before the first and then before the second occurrence).
5. The result can be an empty string. The queue is otherwise unchanged.

## 3. Input specification

`seq`: a non-empty string (its first character is used; an empty `seq` is outside the contract). The queue holds any text, up to about 200,000 characters. Case-insensitive comparison follows `String.regionMatches(true, ...)`, with no locale dependence (so `"ss"` does not match `"ß"`).

## 4. Output specification

The consumed `String`. Examples:
- queue `<textarea>one < two </TEXTarea> third </TEXTarea>`, `seq = "</textarea>"`: returns `<textarea>one < two ` and leaves the queue positioned at `</TEXTarea> third </TEXTarea>`. After the caller removes the matched `</TEXTarea>`, a second call returns ` third `.
- queue `<textarea> one two < three </oops>`, `seq = "</textarea"`: returns the whole text; the queue is then empty.
- queue `abc`, `seq = "ABC"`: returns `""`, position unchanged.
- queue `aAbB`, `seq = "b"`: returns `aA`.

## 5. Edge cases and constraints

- Must run in time roughly linear in the consumed text and terminate for every input.
- Does not throw for any non-empty `seq`; a partial match at the very end of the queue is not a match.

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
TokenQueue::chompBalanced( char open , char close)
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
- `pos` (`int`, private): index into `queue` of the next character to read; characters before it are consumed. Everything from `pos` on is "remaining". The method may change `pos`.

Sibling methods you may call: `isEmpty()` (true when `pos` is at the end); `matches(String seq)` (public; true if the remaining text starts with `seq`, compared ignoring case with `queue.regionMatches(true, pos, seq, 0, seq.length())`); `matchChomp(String seq)` (consumes `seq` if it matches); `remainder()`; `consume()`.

=== STUB ===
```java
public String consumeToIgnoreCase(String seq) {
    // TODO: implement according to the specification
}
```
