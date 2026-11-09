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

## Types and macros the function can use

```
typedef char char_t;
#define PUGI__FN                           // function linkage macro; keep it as in the stub

enum chartype_t { ct_parse_pcdata = 1, ct_parse_attr = 2, ct_parse_attr_ws = 4, ct_space = 8, ct_parse_cdata = 16,
                  ct_parse_comment = 32, ct_symbol = 64, ct_start_symbol = 128 };
#define PUGI__IS_CHARTYPE(c, ct)           // non-zero if byte c belongs to class ct (table lookup, c is an unsigned byte value):
                                           //   ct_space:  ' ', '\t', '\n', '\r'
                                           //   ct_symbol: a-z, A-Z, 0-9, '_', ':', '-', '.', and every byte >= 0x80
```

## Caller (for orientation only)

```
// inside guess_buffer_encoding(const uint8_t* data, size_t size), when the buffer starts with the bytes "<?xm":
const uint8_t* enc = 0; size_t enc_length = 0;
if (parse_declaration_encoding(data, size, enc, enc_length)) { /* compare the name with "latin1", "iso-8859-1" (case-insensitive) */ }
```
