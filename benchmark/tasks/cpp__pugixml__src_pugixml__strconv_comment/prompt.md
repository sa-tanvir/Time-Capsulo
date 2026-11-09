You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level, in the "Parser utilities" section (the macros below are defined right before the function)

## Includes available in this file

```
#include "pugixml.hpp"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
#include <stdint.h>
```

Do not add includes or helper functions.

## Types, macros and helpers the function can use

```
typedef char char_t;                       // character type (this build is not PUGIXML_WCHAR_MODE)
#define PUGI__FN                           // function linkage macro; keep it as in the stub

enum chartype_t { ct_parse_pcdata = 1, ct_parse_attr = 2, ct_parse_attr_ws = 4, ct_space = 8, ct_parse_cdata = 16,
                  ct_parse_comment = 32, ct_symbol = 64, ct_start_symbol = 128 };
#define PUGI__IS_CHARTYPE(c, ct)           // non-zero if character c belongs to class ct (table lookup);
                                           // ct_parse_comment is set for: NUL, '-', '>', '\r'  (the characters a comment scan has to stop at)

// Parser utility macros (defined just above the function; they refer to a variable named `endch` in the enclosing function)
#define PUGI__ENDSWITH(c, e)               ((c) == (e) || ((c) == 0 && endch == (e)))   // c equals e, or c is the NUL terminator and endch equals e
#define PUGI__SCANWHILE_UNROLL(X)          // advances s while the condition X holds; inside X the current character is named `ss`
                                           // (e.g. PUGI__SCANWHILE_UNROLL(!PUGI__IS_CHARTYPE(ss, ct_parse_comment)) skips ordinary characters, unrolled 4x)

// Gap bookkeeping used by the parser to collapse removed characters lazily (existing code, do not modify)
struct gap
{
    char_t* end;     // 0 when there is no gap yet; otherwise the end of the most recently pushed gap
    size_t size;     // total number of characters in all gaps pushed so far

    gap(): end(0), size(0) {}

    // Registers a gap of `count` characters starting at s: first closes the previous gap (moves the text between the end of the
    // previous gap and s back over it), then advances s by count, and remembers the new gap end = s.
    void push(char_t*& s, size_t count);

    // Closes the last gap by moving the text before s back over it; returns the new past-the-end pointer of the text
    // (s itself when there is no gap)
    char_t* flush(char_t* s);
};
```

## Caller (for orientation only)

```
// in xml_parser::parse_exclamation(char_t* s, xml_node_struct* cursor, unsigned int optmsk, char_t endch), after "<!--":
if (PUGI__OPTSET(parse_eol) && PUGI__OPTSET(parse_comments))
{
    s = strconv_comment(s, endch);
    if (!s) PUGI__THROW_ERROR(status_bad_comment, cursor->value);
}
```

=== STUB ===
```cpp
PUGI__FN char_t* strconv_comment(char_t* s, char_t endch)
{
    // TODO: implement according to the specification
}
```
