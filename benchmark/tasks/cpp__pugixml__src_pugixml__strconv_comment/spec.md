# Functional specification: `strconv_comment(s, endch)`

## 1. Component overview

Part of pugixml's parser (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`). When the parser is run with comment
nodes and end-of-line normalization enabled (`parse_comments | parse_eol`) and meets `<!--`, it hands the text that follows to
`strconv_comment`. The function finds the end of the comment, normalizes the line breaks of the comment text **in place** in the
document buffer, terminates the text with a NUL character, and tells the parser where to continue.

## 2. Functional requirements

`s` points at the first character after `<!--` inside a mutable NUL-terminated buffer.

1. **Line break normalization** of the comment text: every carriage return + line feed pair (`\r\n`) becomes a single `\n`; every
   carriage return not followed by a line feed becomes `\n`; other characters are unchanged. (`\r\r` gives two `\n`; `\n\r` gives `\n\n`.)
   The normalized text is stored compactly starting at `s` (it can only become shorter).
2. **End of the comment**: the comment ends at the first position where two consecutive `-` characters are followed by `>`.
   The three characters `-->` are not part of the text. For example in `a--->` the text is `a-` (the first `-` is text, the
   last two form the terminator); `a--b-->` has the text `a--b`; `-->` at the very start gives the empty text.
   - **End-of-buffer special case:** if `endch == '>'`, then `--` followed by the buffer's **NUL terminator** also counts as the
     end of the comment (the parser replaced the final `>` of the document with NUL and passes the original character as
     `endch`). If `endch` is any other character, `--` followed by NUL is not an end.
3. On success the text is terminated in place: the character after the last text character is set to NUL, so that `s`, read as a C
   string, is exactly the normalized comment text. The function returns a pointer just **after the terminator**: three characters
   after the start of `--` when the terminator was `-->` (pointing at whatever follows the `>`), or two characters after the start
   of `--` (pointing at the NUL terminator of the buffer) in the end-of-buffer special case.
4. If the end of the buffer (the NUL terminator) is reached without a terminator, return a null pointer (`0`); the buffer content is then
   unspecified (the parser reports `status_bad_comment`).
5. A `-` or `--` that is not followed as described, a lone `>`, and `--` followed by any other character are ordinary text.

## 3. Input specification

- `s`: `char_t*` (here `char`), into a mutable NUL-terminated buffer; the function may read up to and including the terminating NUL
  and, when it sees `--`, the character after it (never beyond the terminator). The comment text may be many megabytes long.
- `endch`: `char_t`, the character that was originally at the end of the document buffer (usually `>` for a well-formed
  document ending with a comment, otherwise e.g. `<`).

## 4. Output specification

`char_t*`: pointer after the end of the comment (see requirement 3), or `0` when the comment is not terminated. Side effects on success:
normalized text at `s`, NUL-terminated. Nothing is thrown.

## 5. Edge cases and constraints

| content after `<!--` (`endch` = `<` unless noted) | text left at `s` | returns |
|---|---|---|
| `-->` | empty | `s + 3` |
| ` c -->rest` | ` c ` | `s + 6` (at `rest`) |
| `\r\rval1\rval2\r\nval3\nval4\r\r-->` | `\n\nval1\nval2\nval3\nval4\n\n` | after the `>` |
| `a---->` | `a--` | after the `>` |
| `a-->>` | `a` | `s + 4` |
| `-`, `->`, `--`, `-- >`, `no end`, `x\r` | | `0` |
| `abc--` with `endch = '>'` | `abc` | pointer to the NUL (`s + 5`) |
| `abc--` with `endch = 'x'` or `'<'` | | `0` |
| `a-->b--` with `endch = '>'` | `a` | `s + 4` (the first terminator wins) |
| `a-` with `endch = '>'` | | `0` |

Linear time in the length of the comment; plain text without line breaks is the common case and should be scanned quickly.
