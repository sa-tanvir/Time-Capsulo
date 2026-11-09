# Context for the function to implement

- **Language:** java
- **File:** `gson/src/main/java/com/google/gson/stream/JsonReader.java`
- **Enclosing scope:** `public class JsonReader implements Closeable`

## Imports / includes available in this file

```
import com.google.gson.internal.JsonReaderInternalAccess;
import com.google.gson.internal.bind.JsonTreeReader;
import java.io.Closeable;
import java.io.EOFException;
import java.io.IOException;
import java.io.Reader;
import java.util.Arrays;
```

## Other functions defined in the same file (signatures only; you may call them)

```
JsonReader::JsonReader( Reader in)
JsonReader::JsonReaderInternalAccess()
JsonReader::beginArray()
JsonReader::beginObject()
JsonReader::checkLenient()
JsonReader::close()
JsonReader::consumeNonExecutePrefix()
JsonReader::doPeek()
JsonReader::endArray()
JsonReader::endObject()
JsonReader::fillBuffer( int minimum)
JsonReader::getPath()
JsonReader::hasNext()
JsonReader::isLenient()
JsonReader::isLiteral( char c)
JsonReader::locationString()
JsonReader::nextBoolean()
JsonReader::nextDouble()
JsonReader::nextInt()
JsonReader::nextLong()
JsonReader::nextName()
JsonReader::nextNonWhitespace( boolean throwOnEof)
JsonReader::nextNull()
JsonReader::nextQuotedValue( char quote)
JsonReader::nextString()
JsonReader::nextUnquotedValue()
JsonReader::peek()
JsonReader::peekKeyword()
JsonReader::push( int newTop)
JsonReader::readEscapeCharacter()
JsonReader::setLenient( boolean lenient)
JsonReader::skipQuotedValue( char quote)
JsonReader::skipTo( String toFind)
JsonReader::skipToEndOfLine()
JsonReader::skipUnquotedValue()
JsonReader::skipValue()
JsonReader::syntaxError( String message)
JsonReader::toString()
```

## Instance state

`JsonReader` reads characters from a `java.io.Reader` through a fixed-size internal window. Fields the methods use:

- `buffer` (`char[]`, private final, length 1024): the window. Characters `buffer[pos .. limit)` are loaded and not yet consumed.
- `pos` (`int`, private): index in `buffer` of the next unconsumed character.
- `limit` (`int`, private): index one past the last loaded character (`0 <= pos <= limit <= 1024`).
- `lenient` (`boolean`, private): whether non-standard JSON is accepted (see `checkLenient()`).
- `lineNumber` (`int`, private): number of newline characters consumed so far (0-based line index).
- `lineStart` (`int`, private): index in `buffer` at which the current line starts (it may be negative once the window has shifted past the start of the line).
- `peeked` (`int`, package-private): kind of the token already peeked, `PEEKED_NONE` (0) if none.
- `peekedLong` (`long`, private), `peekedNumberLength` (`int`, private): side results of `peekNumber()`.
- `stack`, `stackSize`, `pathNames`, `pathIndices`: the nesting state used only by `getPath()` / `locationString()`.

Sibling methods you may call:

- `fillBuffer(int minimum)` (`boolean`, private; throws `IOException`): discards the consumed characters (shifts `buffer[pos..limit)` to index 0, so afterwards `pos == 0` and `lineStart` has been adjusted accordingly), then reads from the underlying reader until at least `minimum` characters are loaded. Returns `true` if `limit >= minimum` afterwards and `false` if the input ended first. Because it may shift the window, any index you computed from `pos` before the call is invalid afterwards; re-read `pos` and `limit`.
- `isLiteral(char c)` (`boolean`, private): `true` if `c` can be part of an unquoted literal, `false` if it terminates one. Terminators are `{ } [ ] : , space \t \f \r \n`; in addition `/ \ ; # =` are terminators only in lenient mode (in strict mode `isLiteral` throws through `checkLenient()` when it sees them); every other character is a literal character.
- `checkLenient()` (private): throws `MalformedJsonException` (an `IOException`) with message `Use JsonReader.setLenient(true) to accept malformed JSON` + location suffix when `lenient` is false; does nothing otherwise.
- `syntaxError(String message)` (private): throws `MalformedJsonException` with message `message` followed by `locationString()`, i.e. ` at line <lineNumber+1> column <pos - lineStart + 1> path <getPath()>`.

Constants read by `peekNumber()` (all `private static final`):

- `PEEKED_NONE = 0`, `PEEKED_LONG = 15`, `PEEKED_NUMBER = 16`.
- `NUMBER_CHAR_NONE = 0`, `NUMBER_CHAR_SIGN = 1`, `NUMBER_CHAR_DIGIT = 2`, `NUMBER_CHAR_DECIMAL = 3`, `NUMBER_CHAR_FRACTION_DIGIT = 4`, `NUMBER_CHAR_EXP_E = 5`, `NUMBER_CHAR_EXP_SIGN = 6`, `NUMBER_CHAR_EXP_DIGIT = 7` (optional helper states for scanning a number).
- `MIN_INCOMPLETE_INTEGER = Long.MIN_VALUE / 10` (`long`).
