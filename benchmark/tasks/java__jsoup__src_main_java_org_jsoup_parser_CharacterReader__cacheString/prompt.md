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

`CharacterReader.cacheString(charBuf, stringCache, start, count)` builds a `String` from a range of a character buffer, re-using a small hash-indexed cache so that repeated short strings (tag and attribute names) are not allocated again.

## 2. Functional requirements

1. If `count` is greater than the constant `maxStringCacheLen` (12), return a new `String` of `charBuf[start .. start+count)`; the cache is neither read nor changed.
2. If `count` is less than 1, return the empty string `""` and leave the cache alone.
3. Otherwise (`1 <= count <= 12`) the result is always a string equal to `charBuf[start .. start+count)`. Additionally the cache `stringCache` (an array of strings whose length is a power of two, 512 in practice) is used as a direct-mapped cache keyed by the content:
   - compute a hash of the range with the same recurrence as `String.hashCode` (`h = 31*h + c` over the characters, starting at 0, with 32-bit int overflow); the slot is `hash & (stringCache.length - 1)`;
   - if the slot is empty, create the string, store it in the slot and return it;
   - if the slot holds a string with exactly the same characters (checked with the helper `rangeEquals(charBuf, start, count, cached)`), return that stored instance, so requesting the same content twice in a row yields the identical (`==`) object;
   - if the slot holds a different string (a collision), create a new string, replace the slot with it, and return it.
4. The buffer is never modified; only `stringCache` slots can change.

## 3. Input specification

`charBuf`: a non-null `char[]`. `stringCache`: a non-null `String[]` with power-of-two length, initially all `null`, shared across many calls. `start`, `count`: ints with `0 <= start` and `start + count <= charBuf.length` whenever `count > 0`; `count` may be 0 or negative (then the empty string is returned, `start` unused).

## 4. Output specification

A `String`. Examples (buffer `"hello world "`): `(0, 5)` returns `"hello"`; calling it again returns the same instance as the first call; `(6, 5)` returns `"world"`; `(0, 0)` returns `""`; with a 13-character range the result is equal to the characters but is a fresh object every time; `(3, -1)` returns `""`.

## 5. Edge cases and constraints

- Called for every token the tokeniser produces, so it must not allocate on cache hits.
- Not thread-safe (the cache is unsynchronised).

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/jsoup/parser/CharacterReader.java`
- **Enclosing scope:** `public final class CharacterReader`

## Imports / includes available in this file

```
import org.jsoup.UncheckedIOException;
import org.jsoup.helper.Validate;
import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.util.Arrays;
import java.util.Locale;
```

## Other functions defined in the same file (signatures only; you may call them)

```
CharacterReader::CharacterReader( Reader input , int sz)
CharacterReader::CharacterReader( Reader input)
CharacterReader::CharacterReader( String input)
CharacterReader::advance()
CharacterReader::bufferUp()
CharacterReader::consume()
CharacterReader::consumeData()
CharacterReader::consumeDigitSequence()
CharacterReader::consumeHexSequence()
CharacterReader::consumeLetterSequence()
CharacterReader::consumeLetterThenDigitSequence()
CharacterReader::consumeTagName()
CharacterReader::consumeTo( String seq)
CharacterReader::consumeTo( char c)
CharacterReader::consumeToAny( final char ... chars)
CharacterReader::consumeToAnySorted( final char ... chars)
CharacterReader::consumeToEnd()
CharacterReader::containsIgnoreCase( String seq)
CharacterReader::current()
CharacterReader::isBinary()
CharacterReader::isEmpty()
CharacterReader::isEmptyNoBufferUp()
CharacterReader::mark()
CharacterReader::matchConsume( String seq)
CharacterReader::matchConsumeIgnoreCase( String seq)
CharacterReader::matches( String seq)
CharacterReader::matches( char c)
CharacterReader::matchesAny( char ... seq)
CharacterReader::matchesAnySorted( char [ ] seq)
CharacterReader::matchesDigit()
CharacterReader::matchesIgnoreCase( String seq)
CharacterReader::matchesLetter()
CharacterReader::nextIndexOf( CharSequence seq)
CharacterReader::nextIndexOf( char c)
CharacterReader::pos()
CharacterReader::rangeEquals( final char [ ] charBuf , final int start , int count , final String cached)
CharacterReader::rangeEquals( final int start , final int count , final String cached)
CharacterReader::rewindToMark()
CharacterReader::toString()
CharacterReader::unconsume()
```

## Constants and helpers read by the method

- `maxStringCacheLen` (`private static final int`) = 12: longest range that is cached.
- `stringCache` (`String[]`, per `CharacterReader`, length 512, all `null` initially) is the array passed as the argument.
- `static boolean rangeEquals(final char[] charBuf, final int start, int count, final String cached)` (same class): true if `cached` has exactly `count` characters that equal `charBuf[start .. start+count)`.
- The method is `private static`; it has no instance state. It is called by the reader's consume methods, e.g. `cacheString(charBuf, stringCache, start, length)`.

=== STUB ===
```java
private static String cacheString(final char[] charBuf, final String[] stringCache, final int start, final int count) {
    // TODO: implement according to the specification
}
```
