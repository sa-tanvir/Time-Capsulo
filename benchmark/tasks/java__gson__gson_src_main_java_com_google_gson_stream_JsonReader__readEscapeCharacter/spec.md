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
