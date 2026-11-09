# Functional specification

## 1. Component overview

`JsonReader.peekNumber()` is the number-recognition step of the JSON pull parser. The reader's window currently starts, at `buffer[pos]`, with the first character of a value that may be a number. The method decides whether the characters starting there form a complete JSON number literal, and if so classifies it as an integer that fits in a `long` or as some other number, recording the result for the caller (`nextInt`, `nextLong`, `nextDouble`, `nextString`, ...).

## 2. Functional requirements

Scan the characters from `buffer[pos]` (reading more input with `fillBuffer` whenever the loaded part runs out) and match this grammar:

`-? ( 0 | [1-9][0-9]* ) ( . [0-9]+ )? ( [eE] [+-]? [0-9]+ )?`

Rules:

- The literal ends at the first character that is not part of the number **and** is not a literal character (`isLiteral(c) == false`), or at the end of input. The terminator is not consumed.
- If the scan meets a character that cannot continue the grammar at that point (for example a second `-`, a `+` or `.` out of place, `e`/`E` not following a digit, a leading `0` followed by another digit), the result is "not a number".
- If the scan meets any other character that is a literal character (letters, quotes, non-ASCII characters, ...) after or inside the digits, the result is "not a number" (so `12a`, `1x`, `true` are not numbers).
- A lenient-only terminator (`/ \ ; # =`) after the number is handled by `isLiteral`, so in strict mode (`lenient == false`) the `MalformedJsonException` of `checkLenient()` propagates; in lenient mode it simply ends the number.
- The literal must be complete when it ends: the text must end right after a digit of the integer part, of the fraction or of the exponent. `-`, `1.`, `1e`, `1e+`, `.5`, `+1` are not numbers.
- Numbers of 1024 or more characters are not recognised (the result is "not a number"), because the window cannot hold them.

Result, by outcome:

1. **Integer in `long` range** (no fraction, no exponent; optional leading `-`; value between `Long.MIN_VALUE` and `Long.MAX_VALUE` inclusive; but **not** negative zero `-0`): set `peekedLong` to the value (so `-5` gives `-5`, `0` gives `0`, `-9223372036854775808` gives `Long.MIN_VALUE`), advance `pos` past the number, set `peeked = PEEKED_LONG` and return `PEEKED_LONG`.
2. **Any other well-formed number** (has a fraction or exponent, is `-0`, or is an integer outside the `long` range such as `9223372036854775808`, `-9223372036854775809` or a 20-digit integer): set `peekedNumberLength` to the number of characters of the number, set `peeked = PEEKED_NUMBER` and return `PEEKED_NUMBER`. `pos` is **not** advanced in this case.
3. **Not a number**: return `PEEKED_NONE` and leave `pos`, `peeked`, `peekedLong` and `peekedNumberLength` untouched.

## 3. Input specification

No parameters. Input is the reader state described in "Instance state": `buffer[pos..limit)` holds the first loaded characters and further characters can be obtained with `fillBuffer(minimum)`; the first character of the candidate number is `buffer[pos]` (the method may be called when `pos == limit`, in which case more input must be requested first). The underlying `Reader` may deliver few characters per read, so the number can span several fills.

## 4. Output specification

Returns an `int`: `PEEKED_LONG` (15), `PEEKED_NUMBER` (16) or `PEEKED_NONE` (0), with the side effects above. Examples (strict or lenient, whole text available):

- `123,` returns 15, `peekedLong = 123`, `pos` advanced by 3.
- `-9223372036854775808]` returns 15 with `Long.MIN_VALUE`.
- `9223372036854775808` returns 16 with `peekedNumberLength = 19`; `pos` unchanged.
- `-0 ` returns 16, `peekedNumberLength = 2`; `0` returns 15 with value 0.
- `1.5e+3}` returns 16, length 5; `1E5` returns 16, length 3.
- `01`, `-`, `1.`, `1e`, `12abc`, `1-` return 0.

## 5. Edge cases and constraints

- An empty remaining input (`fillBuffer` returns false immediately) returns 0.
- End of input right after the number is a valid terminator (`12` returns 15).
- A character that is lenient-only (`/`, `\`, `;`, `#`, `=`) directly after the digits throws `MalformedJsonException` with message starting `Use JsonReader.setLenient(true) to accept malformed JSON` in strict mode, with `pos`, `peeked` unchanged; in lenient mode the number is accepted.
- `IOException`s thrown by the underlying reader propagate.
- Linear time in the number of characters scanned.
