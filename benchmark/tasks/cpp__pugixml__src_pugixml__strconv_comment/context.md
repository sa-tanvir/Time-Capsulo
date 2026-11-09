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
