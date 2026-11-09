# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level, a function template

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
typedef char char_t;                       // character type (this build is not PUGIXML_WCHAR_MODE)
#define PUGI__FN                           // function linkage macro; keep it as in the stub
#define PUGI__UNSIGNED_OVERFLOW            // attribute macro (empty here); keep it as in the stub
#define PUGI__STATIC_ASSERT(cond)          // compile-time assert

enum chartype_t { ct_parse_pcdata = 1, ct_parse_attr = 2, ct_parse_attr_ws = 4, ct_space = 8, ct_parse_cdata = 16,
                  ct_parse_comment = 32, ct_symbol = 64, ct_start_symbol = 128 };
#define PUGI__IS_CHARTYPE(c, ct)           // non-zero if character c belongs to class ct (table lookup);
                                           // PUGI__IS_CHARTYPE(c, ct_space) is true for ' ', '\t', '\n', '\r'
```

## Callers (signatures only; do not change)

```
PUGI__FN int get_value_int(const char_t* value);            // string_to_integer<unsigned int>(value, (unsigned)INT_MIN, INT_MAX)
PUGI__FN unsigned int get_value_uint(const char_t* value);  // string_to_integer<unsigned int>(value, 0, UINT_MAX)
PUGI__FN long long get_value_llong(const char_t* value);    // string_to_integer<unsigned long long>(value, (unsigned long long)LLONG_MIN, LLONG_MAX)
PUGI__FN unsigned long long get_value_ullong(const char_t* value); // string_to_integer<unsigned long long>(value, 0, ULLONG_MAX)
```
