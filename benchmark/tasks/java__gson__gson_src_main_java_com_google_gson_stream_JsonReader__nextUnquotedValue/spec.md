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
