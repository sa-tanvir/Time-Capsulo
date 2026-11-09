# Functional specification: `pattern_formatter::compile_pattern_(pattern)`

## 1. Component overview

Part of spdlog's pattern formatter. A pattern such as `[%Y-%m-%d %H:%M:%S.%e] [%n] [%^%l%$] %v` mixes literal text with `%`-flags. This function compiles the pattern into the formatter's list of formatter objects (`formatters_`); formatting a message later runs the list in order and concatenates what each element writes.

## 2. Functional requirements

The list `formatters_` is first emptied (compiling replaces any earlier compiled pattern), then it is filled from the characters of `pattern`, scanned from left to right. After the call the list must reproduce the pattern in order when applied to a message:

1. A character that is not `%` and does not belong to a `%` specification is literal text. It appears unchanged in the output, at the position where it occurs relative to the other parts. Consecutive literal characters stay together in order; literal text before a `%` specification is emitted before the output of that specification.
2. A `%` starts a specification: after the `%` the padding specification (optional side `-` or `=` and optional width) is parsed with `handle_padspec_`, which advances the iterator it is given and returns a `padding_info`. The character at the iterator after that is the flag character; it is handled with `handle_flag_(flag, padding)`, which appends the formatter for that flag to the list. The flag character is consumed too, and scanning continues after it.
3. If the pattern ends right after the `%` (with or without a padding specification, e.g. `abc%`, `%5`, `%-`, `%=`), the incomplete specification is dropped: nothing is produced for it. Literal text collected before it is still kept.
4. Everything is decided by `handle_padspec_` and `handle_flag_`: for example `%%` produces one `%`, an unknown flag such as `%y` produces the text `%y`, `%^` and `%$` mark the colour range, and a specification like `%==5v` (a padding with side but no width, then the flag `=`) produces `%=` followed by the literal text `5v`.
5. An empty pattern leaves the list empty (formatting then writes nothing).

## 3. Input specification

`pattern`: a `std::string`, possibly empty, possibly thousands of characters long. It contains no NUL characters.

## 4. Output specification

No return value. The member list `formatters_` holds the compiled pattern; the formatted output of a message (obtained through `format`, which appends the end-of-line string afterwards) is the concatenation of the pieces described above. No exceptions are expected.

## 5. Edge cases and constraints

Examples (UTC, time 2017-07-14 02:40:00.123, thread id 77, logger `main`, level info, payload `hello`, empty end-of-line):

| pattern | output |
|---|---|
| (empty) | (empty) |
| `%v` | `hello` |
| `%%` | `%` |
| `%` | (empty) |
| `abc%` | `abc` |
| `%]` | `%]` |
| `%5` | (empty) |
| `%y` | `%y` |
| `[%Y-%m-%d %H:%M:%S.%e] [%n] [%l] %v` | `[2017-07-14 02:40:00.123] [main] [info] hello` |
| `%-10l\|%=8L\|%12n\|%v` | `info      \|   I    \|        main\|hello` |
| `%x %X` | `07/14/17 02:40:00` |
| `%12v` | `       hello` |
| `ab%^cd%$ef` | `abcdef` (colour range marks the output offsets 2 to 4) |
| `%==5v` | `%=5v` |

The pattern is compiled once per formatter, but may be long, so the cost must be linear in the pattern length.
