# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }`
- **Enclosing scope:** the body of `struct utf8_decoder { typedef uint8_t type; ... };` (a struct with only static members; `process` is its only function)

## Includes available in this file

```
#include "pugixml.hpp"
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
#include <stdint.h>
```

Do not add includes or helper functions.

## Instance state

None: `utf8_decoder` has no data members; `process` is a static member function template and the `Traits` object argument is only used for template argument deduction.

## The `Traits` policies (existing code; `process` is instantiated with all of these)

```
struct utf16_counter { typedef size_t value_type;   // counts UTF-16 code units
    static value_type low(value_type result, uint32_t) { return result + 1; }
    static value_type high(value_type result, uint32_t) { return result + 2; } };

struct utf16_writer { typedef uint16_t* value_type;  // writes UTF-16 code units, returns pointer past them
    static value_type low(value_type result, uint32_t ch);    // *result = ch; return result + 1
    static value_type high(value_type result, uint32_t ch);   // writes a surrogate pair, returns result + 2
};

struct utf32_writer  { typedef uint32_t* value_type; static value_type low(value_type, uint32_t ch); static value_type high(value_type, uint32_t ch); };  // one uint32_t per call
struct latin1_writer { typedef uint8_t*  value_type; static value_type low(value_type, uint32_t ch); static value_type high(value_type, uint32_t ch); };  // one byte per call ('?' if not representable)
struct utf8_writer   { typedef uint8_t*  value_type; static value_type low(value_type, uint32_t ch); static value_type high(value_type, uint32_t ch); };  // re-encodes as UTF-8
struct utf8_counter, utf32_counter;                                           // size_t counters
```

The call site in the library (for orientation): `utf8_decoder::process(data, size, dest, utf16_writer())`.
