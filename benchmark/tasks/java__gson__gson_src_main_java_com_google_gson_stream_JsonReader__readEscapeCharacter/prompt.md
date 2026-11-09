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

`JsonReader.readEscapeCharacter()` decodes one backslash escape sequence inside a quoted JSON string. The backslash has already been consumed: `buffer[pos]` is the character right after it. The method consumes the rest of the escape sequence and returns the character it denotes.

## 2. Functional requirements

Let `e` be the character at `pos` (if no character is loaded, read more input first with `fillBuffer(1)`; if the input has ended, fail as described below). Consume `e`, then:

| `e` | result |
|---|---|
| `u` | the next four characters must be hexadecimal digits (`0-9`, `a-f`, `A-F`, either case); consume them and return the `char` whose code is that 16-bit value (e.g. `u00e9` gives `\u00e9`, `u20AC` gives `\u20ac`, `uD83D` gives the high surrogate `\ud83d`) |
| `t`, `b`, `n`, `r`, `f` | tab, backspace, line feed, carriage return, form feed |
| a line feed `\n` (an escaped real newline) | return `\n`, and record that a new line started: `lineNumber` is incremented and `lineStart` is set to the index of the character following it (`pos` after consuming) |
| `'`, `"`, `\`, `/` | the same character |
| anything else | invalid escape |

Errors (all leave the characters consumed so far consumed, as stated):

- End of input where the escape character is expected (nothing left after the backslash): throw `MalformedJsonException` with message `Unterminated escape sequence` + location suffix (see `syntaxError`).
- `u` followed by fewer than four characters before the end of input: the `u` is consumed; throw `MalformedJsonException` with message `Unterminated escape sequence` + location suffix.
- `u` followed by four characters of which at least one is not a hexadecimal digit: the `u` is consumed (the four characters are not); throw `NumberFormatException` whose message is `\u` (a backslash and `u`) followed by those four characters (e.g. `\u000g`).
- Any other character `e` (for example `q`, `x`, `0`, a space, a carriage return): `e` is consumed; throw `MalformedJsonException` with message `Invalid escape sequence` + location suffix.

## 3. Input specification

No parameters. Reader state as described in "Instance state"; the characters after the backslash may not be loaded yet, and the underlying `Reader` may deliver them in very small pieces (a `u` escape may be split across reads).

## 4. Output specification

Returns the decoded `char`. Examples (text after the backslash):

- `n"abc` returns `\n`, with `pos` just after the `n`.
- `u0041x` returns `A`; `u20AC` returns the euro sign.
- `"` returns `"`; `/` returns `/`; `\` returns a backslash.
- an escaped newline returns `\n` and increments `lineNumber`.
- `q` throws `MalformedJsonException` `Invalid escape sequence at line 1 column 2 path $` (for a fresh reader positioned at the start of the text).
- `u12` then end of input throws `MalformedJsonException` `Unterminated escape sequence at line 1 column 2 path $`.

## 5. Edge cases and constraints

- Exceptions: `MalformedJsonException` (an `IOException`), `NumberFormatException`, and `IOException` from the underlying reader.
- The location suffix is computed from `pos` at the time of the error, so the number of characters consumed before throwing matters (see above).
- Constant time.

=== CONTEXT ===
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
JsonReader::peekNumber()
JsonReader::push( int newTop)
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

`lineNumber` and `lineStart` are updated by this method (see the specification). `NumberFormatException` is `java.lang.NumberFormatException`.

=== STUB ===
```java
private char readEscapeCharacter() throws IOException {
    // TODO: implement according to the specification
}
```
