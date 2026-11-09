You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `convert_number_to_string(value, alloc)`

## 1. Component overview

Part of pugixml's XPath engine (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`). It implements the XPath
`string()` conversion of a number (XPath 1.0, section 4.2): `string(0.5)`, `concat('x', 1 div 3)`, `string(1 div 0)`,
and so on. The result is an `xpath_string` (the engine's string value type, see context), whose text must live in memory taken
from the engine's `xpath_allocator` `alloc` (so that it stays valid for the duration of the query evaluation).

## 2. Functional requirements

1. Special values give constant strings (no allocation):
   - NaN -> `NaN`; positive infinity -> `Infinity`; negative infinity -> `-Infinity`;
   - positive or negative zero -> `0` (negative zero gets no sign).
2. Any other (finite, non-zero) value is written in plain decimal notation, **never in exponent notation**:
   a. The value is first rounded to 16 significant decimal digits (exactly the digits that `printf("%.15e")`, i.e.
      `DBL_DIG + 1` significant digits, produces) and trailing zeros of that digit string are dropped. No further digits are
      shown, even for huge integers: the digits beyond the 16th are written as `0`.
   b. A negative value starts with `-`.
   c. Write the value as `0.d1d2...dk * 10^e` with `d1 != 0` and the trailing-zero-free digit string `d1..dk` (`1 <= k <= 16`):
      - integer part: if `e > 0`, the first `e` digits (padded on the right with `0` when `k < e`); otherwise the single digit `0`;
      - fractional part: if there are digits not yet written (`k > e`), a decimal point followed by `-e` zeros (only when `e < 0`) and then
        the remaining digits; otherwise no decimal point is written at all.
3. For case 2 the returned text is NUL-terminated and stored in a buffer obtained from `alloc->allocate(bytes)`
   (`bytes` = characters including the terminator times `sizeof(char_t)`). The buffer must be big enough for the longest
   results (309 characters for `1.7976931348623157e308`, 341 for the denormal `5e-324`).
4. If `alloc->allocate` returns null (out of memory) the function returns an **empty** `xpath_string` (default-constructed). This
   applies to case 2 only; special values (case 1) never allocate and are returned even when the allocator is exhausted.

## 3. Input specification

- `value`: `double`, any IEEE-754 value including NaN, infinities, zeros and denormals.
- `alloc`: `xpath_allocator*`, never null; `allocate(size)` returns suitably aligned memory, or null when it cannot.

## 4. Output specification

An `xpath_string` whose `c_str()` is the text defined above (empty string on allocation failure). The `xpath_string`
factory functions in context build it: `from_const` for constant text, `from_heap_preallocated` for text written into allocator memory.

## 5. Edge cases and constraints

| value | result |
|---|---|
| `0`, `-0` | `0` |
| `1`, `-1`, `10`, `100`, `123456789` | `1`, `-1`, `10`, `100`, `123456789` |
| `0.5`, `-0.5`, `0.1`, `0.25`, `1.5`, `100.25`, `12.375` | `0.5`, `-0.5`, `0.1`, `0.25`, `1.5`, `100.25`, `12.375` |
| `0.3` (binary value 0.299999999999999988...) | `0.3` |
| `1/3` | `0.3333333333333333` |
| `0.000001`, `1e-7` | `0.000001`, `0.0000001` |
| `1e15`, `1e16`, `1e21` | `1000000000000000`, `10000000000000000`, `1000000000000000000000` |
| `1234567890123456` | `1234567890123456` |
| `12345678901234567` (the double 12345678901234568) | `12345678901234570` |
| `2^60` (1152921504606846976) | `1152921504606847000` |
| `-987.654321` | `-987.654321` |
| `1.7976931348623157e308` (DBL_MAX) | `1797693134862316` followed by 293 zeros |
| `5e-324` (smallest denormal) | `0.` followed by 323 zeros and then `4940656458412465` |
| NaN, `+inf`, `-inf` | `NaN`, `Infinity`, `-Infinity` |

The function is called once for every number-to-string conversion in a query, so it is on the hot path of string-heavy
XPath evaluation: avoid unnecessary passes over the digits.

=== CONTEXT ===
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

=== STUB ===
```cpp
PUGI__FN xpath_string convert_number_to_string(double value, xpath_allocator* alloc)
{
    // TODO: implement according to the specification
}
```
