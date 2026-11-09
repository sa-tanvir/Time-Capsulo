# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level, in the XPath implementation section

## Includes available in this file

```
#include "pugixml.hpp"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <math.h>
#include <float.h>
```

Do not add includes or helper functions.

## Types and helpers the function can use

```
typedef char char_t;                       // character type (this build is not PUGIXML_WCHAR_MODE)
#define PUGI__FN                           // function linkage macro; keep it as in the stub
#define PUGIXML_TEXT(t) t                  // string literal macro (narrow build)

struct xpath_allocator
{
    void* allocate(size_t size);           // returns suitably aligned memory (rounded up internally), or 0 when out of memory
    void* reallocate(void* ptr, size_t old_size, size_t new_size);
};

class xpath_string                         // value type; cheap to copy; does not own constant strings
{
public:
    xpath_string();                                                         // the empty string
    static xpath_string from_const(const char_t* str);                      // refers to a NUL-terminated constant string (not copied)
    static xpath_string from_heap_preallocated(const char_t* begin, const char_t* end);
                                                                            // text in allocator memory [begin, end), *end must be the NUL terminator
    const char_t* c_str() const;
    size_t length() const;
    bool empty() const;
    void append(const xpath_string& o, xpath_allocator* alloc);
};

// existing helpers for number formatting
PUGI__FN const char_t* convert_number_to_string_special(double value);
    // returns "NaN", "Infinity", "-Infinity" or "0" (for +0 and -0) as constant strings; returns 0 for every other (finite, non-zero) value

PUGI__FN void convert_number_to_mantissa_exponent(double value, char (&buffer)[32], char** out_mantissa, int* out_exponent);
    // for a finite non-zero value: writes into buffer the 16 significant digits (trailing zeros removed, sign skipped, NUL-terminated),
    // sets *out_mantissa to the first digit (inside buffer; for a negative value buffer[0] is '-' and the digits start after it) and
    // *out_exponent to e such that |value| ~= 0.DIGITS * 10^e
```

## Callers (for orientation only)

```
// xpath_ast_node::eval_string(...) for number-typed expressions:
//     case xpath_type_number: return convert_number_to_string(eval_number(c, stack), stack.result);
```
