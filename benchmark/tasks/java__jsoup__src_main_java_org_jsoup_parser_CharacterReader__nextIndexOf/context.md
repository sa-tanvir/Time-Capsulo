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
