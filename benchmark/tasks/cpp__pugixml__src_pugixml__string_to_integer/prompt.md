You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `string_to_integer<U>(value, minv, maxv)`

## 1. Component overview

Part of pugixml's DOM layer (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`). It converts the text of an
attribute or node value into an integer, in the way `as_int()`, `as_uint()`, `as_llong()` and `as_ullong()` do. One
function template serves all four: `U` is always an **unsigned** integer type (`unsigned int` or `unsigned long long`;
sizes 2, 4 or 8 bytes are all valid), and the caller passes the lowest and highest result of the *target* type, expressed in `U`.
For example `as_int` calls `string_to_integer<unsigned int>(s, static_cast<unsigned int>(INT_MIN), INT_MAX)`, so a negative
result is returned as its two's-complement bit pattern in `U`; `as_uint` passes `(s, 0, UINT_MAX)`. The function never fails:
unparsable text gives 0 and out-of-range values saturate.

## 2. Functional requirements

1. Skip leading whitespace: any number of the characters space, tab (`\t`), line feed (`\n`) and carriage return (`\r`).
2. Read an optional single sign character, `+` or `-`. Only one sign is consumed; a second sign, or whitespace after the
   sign, ends the number (so no digits follow).
3. Read the magnitude:
   - if the next two characters are `0` followed by `x` or `X`, the magnitude is hexadecimal: the prefix is consumed and
     then hexadecimal digits `0-9`, `a-f`, `A-F` follow;
   - otherwise the magnitude is decimal digits `0-9`. A leading `0` is **not** an octal prefix (`"0777"` is 777).
   - The digits end at the first character that is not a valid digit of that base; anything after is ignored
     (`"12abc"` -> 12, `"0xzz"` -> 0, `"1e5"` -> 1). `"0x"` with no digits has magnitude 0. If there are no digits at all
     the magnitude is 0.
   - Any number of leading zeros is allowed (even millions of them); they do not count towards the overflow check.
4. The magnitude is the mathematical value of the digits. It **overflows** if it does not fit in `U` (i.e. is larger than the
   largest value of `U`, 2^(8*sizeof(U)) - 1).
5. Result for a **non-negative** number (no sign or `+`): `maxv` if the magnitude overflows or is greater than `maxv`;
   otherwise the magnitude.
6. Result for a **negative** number (`-`): `minv` if the magnitude overflows or the magnitude is greater than the absolute
   value of `minv` (that is `0 - minv` evaluated in `U`; for `minv == 0` every non-zero magnitude is too large);
   otherwise the negated magnitude, in `U` arithmetic (`0 - magnitude`, wrapping). `-0` gives 0.
7. The function reads the string up to its terminating NUL only and does not modify it.

## 3. Input specification

- `value`: `const char_t*` (here `char_t` is `char`), NUL-terminated, never null. It may be empty, may start with
  whitespace, may contain any bytes after the number and may contain very long digit or zero runs (up to millions of
  characters).
- `minv`, `maxv`: values of type `U`. `maxv` is the highest valid result; `minv` is the lowest valid result (0 for unsigned
  targets, the two's-complement pattern of the signed minimum for signed targets). Callers use the pairs
  `(INT_MIN as unsigned, INT_MAX)`, `(0, UINT_MAX)`, `(LLONG_MIN as unsigned long long, LLONG_MAX)`, `(0, ULLONG_MAX)`.

## 4. Output specification

A value of type `U` as defined in requirements 5 and 6. No exceptions are thrown; there is no error indication.

## 5. Edge cases and constraints

Examples with `U = unsigned int, minv = (unsigned)INT_MIN, maxv = INT_MAX` (signed 32-bit view of the result):

| input | result |
|---|---|
| `""`, `"abc"`, `"+"`, `"- 1"` | 0 |
| `"  \t42"` | 42 |
| `"+1"`, `"+0xa"` | 1, 10 |
| `"0777"` | 777 |
| `"0x5ab"`, `"0XFf"` | 1451, 255 |
| `"-0x20"` | -32 |
| `"-0x80000000"`, `"-2147483648"` | INT_MIN |
| `"2147483648"`, `"0x80000000"` | INT_MAX (saturated) |
| `"-2147483649"`, `"-4294967296"`, `"-0x80000001"` | INT_MIN (saturated) |
| `"21474836479"` | INT_MAX |
| `"0x"` | 0 |
| 48 zeros followed by `1`; `"0x"` + 48 zeros + `1` | 1 |

With `U = unsigned int, minv = 0, maxv = UINT_MAX`: `"-1"` -> 0, `"-0x1"` -> 0, `"4294967295"` and `"0xFFFFFFFF"` ->
4294967295, `"4294967296"`, `"5294967295"`, `"0x100000000"`, `"0x123456789"` -> 4294967295 (saturated).
With `U = unsigned long long`: `"9223372036854775808"` with `maxv = LLONG_MAX` -> LLONG_MAX; `"18446744073709551616"`,
`"28446744073709551615"`, `"166020696663385964543"` with `maxv = ULLONG_MAX` -> ULLONG_MAX; `"-1"` with `minv = 0` -> 0.

Take care that overflow is detected exactly, including numbers whose length equals the maximum digit count of `U`
(e.g. `"4999999999"` and `"4300000000"` overflow a 32-bit `U`, `"4200000000"` does not; `"19000000000000000000"` overflows a
64-bit `U`) and that wrapped intermediate arithmetic cannot make an overflowing value look valid. Running time must be
linear in the length of the string, with a small constant: inputs of more than a million characters are processed.

=== CONTEXT ===
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

=== STUB ===
```cpp
template <typename U> PUGI__FN PUGI__UNSIGNED_OVERFLOW U string_to_integer(const char_t* value, U minv, U maxv)
{
    // TODO: implement according to the specification
}
```
