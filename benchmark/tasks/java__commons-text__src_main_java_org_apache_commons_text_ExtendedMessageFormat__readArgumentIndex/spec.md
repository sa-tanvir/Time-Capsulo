# Functional specification

## 1. Component overview

`ExtendedMessageFormat.readArgumentIndex(pattern, pos)` parses the argument index of a format element in a `MessageFormat`-style pattern (the `0` in `{0,number}` or `{0}`), starting at the cursor `pos`. The opening brace has already been consumed by the caller. It returns the index and leaves the cursor at the character that terminated the number.

## 2. Functional requirements

1. Remember the starting cursor index as `start`, then skip any whitespace characters at the cursor (advance the cursor over them).
2. Read characters one at a time from the cursor, advancing the cursor after each character that is consumed:
   - If the current character is whitespace: skip all whitespace, then look at the character now under the cursor. It must be `,` or `}`; otherwise this is an error (invalid index). (Whitespace is allowed before the terminator, but not between digits.)
   - If the current character (after such skipping) is `,` or `}` **and** at least one character has been collected, the collected text is parsed as a decimal integer and returned; the cursor stays on the terminator (it is not advanced past it). If the collected text does not fit into an `int`, parsing fails silently: the terminator is then treated like any other character (it is non-numeric, so the invalid-index error below results).
   - Otherwise the character is collected; if it is not a decimal digit (`Character.isDigit`), this is an error (invalid index) and reading stops, with the offending character included in the text reported.
3. If an error occurred, throw `IllegalArgumentException` with the message `Invalid format argument index at position <start>: <text>` where `<text>` is the substring of `pattern` from `start` up to (not including) the cursor position at the moment of the failure.
4. If the end of the pattern is reached without a terminator and without an error, throw `IllegalArgumentException` with the message `Unterminated format element at position <start>`.

## 3. Input specification

`pattern`: a non-null string; `pos`: a `ParsePosition` whose index is within `0..pattern.length()`. The text from the cursor onward is expected to look like `[whitespace]digits[whitespace]` followed by `,` or `}`. Patterns that end in whitespace directly after the cursor are outside the contract.

## 4. Output specification

An `int` (non-negative for digit strings, leading zeros allowed) and the cursor advanced to the terminator. Examples with cursor 0: `"0}"` returns 0, cursor 1; `"12 ,x}"` returns 12, cursor 3; `" 7 }"` returns 7, cursor 3; `"007,"` returns 7, cursor 3. Errors: `"1a}"` throws `Invalid format argument index at position 0: 1a`; `"1 2}"` throws `Invalid format argument index at position 0: 1 2`; `"}"` and `","` throw `Invalid format argument index at position 0: }` / `: ,` (nothing collected yet, so the terminator is an invalid index); `"99999999999}"` (too large for an int) throws `Invalid format argument index at position 0: 99999999999}`; `"12"` throws `Unterminated format element at position 0`.

## 5. Edge cases and constraints

- Only the cursor of `pos` is modified, and it is also advanced when an exception is thrown.
- A negative sign is not accepted (`-` is not a digit).
- The method is stateless and thread-safe apart from the shared `ParsePosition`.
