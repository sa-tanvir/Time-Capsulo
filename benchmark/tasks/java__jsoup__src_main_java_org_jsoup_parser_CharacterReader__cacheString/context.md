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
