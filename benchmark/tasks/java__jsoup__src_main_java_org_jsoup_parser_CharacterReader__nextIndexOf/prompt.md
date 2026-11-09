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

`CharacterReader.nextIndexOf(seq)` reports how far ahead of the current read position the next occurrence of a character sequence lies, without consuming anything.

## 2. Functional requirements

The reader holds an internal window (buffer) of the input: positions `bufPos` (the current read position) up to `bufLength` (exclusive) are the characters currently available. Input shorter than the buffer capacity (32768 characters, which includes all inputs in this task) lives entirely in the buffer.

1. First make sure the buffer is current by calling the reader's buffer-refill routine `bufferUp()` (it may reload the window when the read position has advanced past the refill threshold; for short inputs it changes nothing).
2. Search the buffered characters from `bufPos` for the first occurrence of `seq` (exact, case-sensitive character match, `seq` taken as `char` units; no surrogate-pair handling). The occurrence must lie completely inside the buffer, i.e. end at or before `bufLength`.
3. Return the offset of the first character of the first such occurrence relative to the current position (`index - bufPos`, so `0` means the sequence starts at the current position). Return `-1` if there is none, including when `seq` is longer than the remaining buffered text.
4. Overlapping or partial earlier matches must not hide a later full match (e.g. `aab` is found at offset 2 in `aaaab`).
5. The reader's position and state are not changed by the search.

## 3. Input specification

`seq`: a non-empty `CharSequence` (the first character is read unconditionally, so an empty sequence is outside the contract). The reader was created from a string of up to a few tens of thousands of characters (no NUL characters), and may already have been advanced by calling `advance()`.

## 4. Output specification

An `int`, `-1` or `>= 0`. Examples with the reader over `abcabcabc`:
- position 0, `abc` returns 0; after one `advance()`, `abc` returns 2; after two advances, `cab` returns 0.
- position 0, `c` returns 2; position 0, `z` returns -1; `abcabcabcd` returns -1.
- after three advances, `c` returns 2.

## 5. Edge cases and constraints

- Hot method of the tokeniser: it must not allocate and should be roughly linear in the remaining text.
- Single-character sequences are valid and behave like a character search.

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
CharacterReader::cacheString( final char [ ] charBuf , final String [ ] stringCache , final int start , final int count)
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
CharacterReader::nextIndexOf( char c)
CharacterReader::pos()
CharacterReader::rangeEquals( final char [ ] charBuf , final int start , int count , final String cached)
CharacterReader::rangeEquals( final int start , final int count , final String cached)
CharacterReader::rewindToMark()
CharacterReader::toString()
CharacterReader::unconsume()
```

## Instance state

Fields of `CharacterReader` used by the method:

- `charBuf` (`char[]`, private final): the buffer, with capacity `min(input length, 32768)`.
- `bufLength` (`int`): number of valid characters in `charBuf` (valid indexes are `0 .. bufLength-1`).
- `bufPos` (`int`): index in `charBuf` of the current character (the next one to consume).
- `bufSplitPoint`, `readerPos`, `reader`: refill bookkeeping, only touched by the private method `bufferUp()`, which refills the buffer from the underlying reader when `bufPos >= bufSplitPoint`. For inputs shorter than 24576 characters, `bufferUp()` never changes `bufPos`, `bufLength` or `charBuf` while there is nothing left to read.

Sibling methods you may call: `nextIndexOf(char c)` (single character search), `advance()` (increments `bufPos`), `isEmpty()`, `current()`, `consume()`.

=== STUB ===
```java
int nextIndexOf(CharSequence seq) {
    // TODO: implement according to the specification
}
```
