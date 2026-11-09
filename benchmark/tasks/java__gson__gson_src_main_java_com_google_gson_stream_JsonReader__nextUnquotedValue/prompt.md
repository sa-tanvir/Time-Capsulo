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

`JsonReader.nextUnquotedValue()` reads an unquoted literal (a bare word such as `true`, `abc`, `12ab`, `-Infinity`) from the reader's window and returns it as a `String`, consuming it. It is used for unquoted names and values, which JSON only allows in lenient mode, and for literals that are not valid numbers.

## 2. Functional requirements

Starting at `buffer[pos]`, collect consecutive characters until the first terminator character or the end of input. A terminator is any character for which `isLiteral(c)` would return `false`: `{ } [ ] : , space \t \f \r \n`, plus the lenient-only characters `/ \ ; # =`.

- When the scan reaches a lenient-only character (`/`, `\`, `;`, `#`, `=`), it must call `checkLenient()`: in strict mode (`lenient == false`) this throws `MalformedJsonException` (message starts with `Use JsonReader.setLenient(true) to accept malformed JSON`); in lenient mode the character just terminates the literal.
- The returned string consists of exactly the collected characters (it may be empty if the first character is already a terminator, or if the input is exhausted).
- On return, `pos` points at the terminator (or at `limit` if the input ended): the literal is consumed, the terminator is not.
- Literals may be arbitrarily long, much longer than the 1024-char window; the method must deliver the whole literal, reading more input with `fillBuffer` as needed.
- The underlying `Reader` may return only a few characters per read; the result must not depend on how the input is chunked.
- Does not touch `lineNumber`/`lineStart` or `peeked`: those are handled by the caller.

## 3. Input specification

No parameters. The input is the reader state described in "Instance state": `buffer[pos..limit)` holds already loaded characters (possibly none) and more can be obtained from the underlying reader with `fillBuffer(minimum)`. Characters can be any `char`.

## 4. Output specification

Returns the literal as a `String`. Examples (lenient or not, unless noted):

- remaining input `abc,def` returns `abc`, with `pos` at the `,`.
- `true]` returns `true`; `12ab ` returns `12ab`.
- `x` (end of input) returns `x`, with all input consumed.
- remaining input `,abc` returns `""` and consumes nothing.
- `a/b` in lenient mode returns `a`; in strict mode throws `MalformedJsonException`.
- A literal of 5000 characters followed by `]` returns all 5000 characters.

## 5. Edge cases and constraints

- Throws `MalformedJsonException` only for the lenient-only characters in strict mode (see above). `IOException`s of the underlying reader propagate.
- Linear in the length of the literal; avoid quadratic copying for very long literals.
- When an exception is thrown the position of `pos` is unspecified.

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
JsonReader::peek()
JsonReader::peekKeyword()
JsonReader::peekNumber()
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

=== STUB ===
```java
private String nextUnquotedValue() throws IOException {
    // TODO: implement according to the specification
}
```
