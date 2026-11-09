# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level

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

## Types and helpers the function can use

```
typedef char char_t;      // character type (this build is not PUGIXML_WCHAR_MODE)
#define PUGI__FN          // function linkage macro; keep it as in the stub

// Gap bookkeeping used by the parser to collapse decoded entities lazily (existing code, do not modify)
struct gap
{
    char_t* end;     // 0 when there is no gap yet; otherwise the end of the most recently pushed gap
    size_t size;     // total number of bytes in all gaps pushed so far

    gap(): end(0), size(0) {}

    // Push a new gap of `count` bytes starting at s: collapses the previous gap (moves the text between the end
    // of the previous gap and s back over it), then advances s by count, and remembers the new gap end = s.
    void push(char_t*& s, size_t count);

    // Collapses the last gap and returns the new past-the-end pointer of the text
    char_t* flush(char_t* s);
};

struct utf8_writer
{
    typedef uint8_t* value_type;
    // Writes the UTF-8 encoding of ch (1 byte below 0x80, 2 below 0x800, 3 below 0x10000, otherwise 4) at result
    // and returns the pointer past the written bytes.
    static value_type any(value_type result, uint32_t ch);
};
```

## How the function is called (for orientation only)

```
// inside the pcdata / attribute parsers, with `gap g;` declared by the caller:
if (*s == '&') s = strconv_escape(s, g);   // otherwise ++s
...
end = g.flush(s);                          // at the end of the text
```
