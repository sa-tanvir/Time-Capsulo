# Functional specification

## 1. Component overview

`JsonReader.skipUnquotedValue()` advances the reader past an unquoted literal (a bare word such as `true`, `abc`, `12ab`) without building a string. It is used when skipping values and names.

## 2. Functional requirements

Starting at `buffer[pos]`, consume consecutive characters up to, but not including, the first terminator character, or up to the end of input. A terminator is any character for which `isLiteral(c)` would return `false`: `{ } [ ] : , space \t \f \r \n`, plus the lenient-only characters `/ \ ; # =`.

- When the scan reaches a lenient-only character (`/`, `\`, `;`, `#`, `=`), it must call `checkLenient()`: in strict mode (`lenient == false`) this throws `MalformedJsonException` (message starts with `Use JsonReader.setLenient(true) to accept malformed JSON`); in lenient mode the character just terminates the literal.
- The literal can be arbitrarily long, much longer than the 1024-char window: when the loaded characters are all literal characters, discard them and load more input (`fillBuffer`), until a terminator or the end of input is found.
- The result must not depend on how the underlying `Reader` chunks its input.
- `lineNumber`, `lineStart` and `peeked` are not changed.

## 3. Input specification

No parameters. The input is the reader state described in "Instance state": `buffer[pos..limit)` holds already loaded characters (possibly none) and more can be obtained with `fillBuffer(minimum)`.

## 4. Output specification

No return value. Afterwards, the next unconsumed character is the terminator that ended the literal, or the input is completely consumed. Examples:

- remaining input `abc,def`: after the call the next character is `,`.
- `true]`: the next character is `]`. `12ab ` : the next character is the space.
- `x` then end of input: all input consumed, no exception.
- `,abc`: nothing is consumed.
- `a/b` in lenient mode: the next character is `/`; in strict mode `MalformedJsonException` is thrown.
- A literal of 5000 characters followed by `]`: the next character is that `]`.

## 5. Edge cases and constraints

- Throws `MalformedJsonException` only for the lenient-only characters in strict mode. `IOException`s of the underlying reader propagate.
- Linear in the length of the literal.
- When an exception is thrown the position of `pos` is unspecified.
