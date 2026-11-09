You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `IsHexFloatString(start, end, separator, allow_trailing_junk)`

## 1. Component overview

`StringToDoubleConverter` in the double-conversion library can read hexadecimal floating-point literals such as `0x1.8p3` (the C99 / Java style: hexadecimal mantissa, binary exponent introduced by `p`). Before the number is converted, `IsHexFloatString` checks that the text after the `0x` / `0X` prefix really is a hex float; the prefix itself has already been consumed by the caller and is not part of the range. The function is a pure validator: it only reads the range and answers `true` or `false`.

## 2. Functional requirements

The text in `[start, end)` is valid when it has this shape:

```
mantissa  :=  hexdigit+                 |   hexdigit* '.' hexdigit+   |   hexdigit+ '.'
literal   :=  mantissa ('p' | 'P') ('+' | '-')? decdigit+   [ trailing part ]
```

1. `hexdigit` is `0-9`, `a-f`, `A-F`. `decdigit` is `0-9`. At least one hex digit must exist in the mantissa (before or after the point); a point alone (`".p0"`), or no mantissa at all (`"p0"`), is invalid. A mantissa with a point but no digits after it (`"1.p0"`) is valid. At most one point is allowed. `0x` is not part of the text.
2. The exponent marker `p` or `P` is required. The exponent consists of an optional sign followed by at least one decimal digit; `"1p"`, `"1p+"`, `"1p-"` and a missing marker (`"1"`, `"1."`, `"1.0"`) are invalid. Exponent digits are decimal only (hex letters are not exponent digits).
3. Trailing part: when the exponent digits stop before the end of the range, the text is valid if `allow_trailing_junk` is `true` (anything may follow), or if all remaining characters are white space (using the helper `isWhitespace`). Otherwise it is invalid. If the range ends immediately after an exponent digit, it is valid.
4. A range that ends anywhere before the first exponent digit has been read (inside the mantissa, right after the point, right after `p`, or right after the sign) is invalid. No character at or beyond `end` may be read.
5. Separator: when `separator` is not `StringToDoubleConverter::kNoSeparator` (the character code 0), a single separator character that is directly between two digits is skipped transparently: this applies wherever the scanner moves from a digit to the next character, in the mantissa and also in the exponent, and "digit" here means a hexadecimal digit for the character before and after the separator, wherever it occurs. A separator in any other position (at the start, next to the point or the exponent marker or the sign, doubled, at the end) is an ordinary character that does not belong to the number. The helper `Advance` in the context implements exactly this movement and tells you when the end of the range has been reached.
6. The result depends only on the characters; case (`p` / `P`, `a-f` / `A-F`) does not matter.

## 3. Input specification

- `start`, `end`: iterators of the same type (`const char*` or `const uc16*`, `uc16` is a 16-bit unsigned character type); characters are compared as integer code points, any code of 128 or above is simply not a digit. `start != end` (the range is not empty).
- `separator`: `uc16`, the separator character code or 0 for none.
- `allow_trailing_junk`: `bool`.

## 4. Output specification

`true` when the range is a valid hex float (item 3 and 4 decide where it may end), else `false`. No exceptions, no output parameters. The range is not modified.

## 5. Edge cases and constraints

| text | separator | allow_trailing_junk | result |
|---|---|---|---|
| `1p0` / `1P0` | none | any | true |
| `1.p0`, `.1p0`, `abcdefp12`, `0p0`, `1p01` | none | any | true |
| `.p0`, `p0`, `1`, `1.`, `1.0`, `1p`, `1p+`, `1p-` | none | any | false |
| `1p+1`, `1p-1` | none | any | true |
| `1.8p1 ` (one trailing space) | none | false | true |
| `1.8p1x` | none | false / true | false / true |
| `1.8p1 x` | none | false / true | false / true |
| `g1p1`, `1gp1`, `1p1p1`, `1.2.3p1`, `1 p1`, `1p 1`, `1.p` | none | any | false |
| `1_2p3` | `_` | false | true |
| `1_2_3.4_5p6_7` | `_` | false | true |
| `1_.2p3`, `1._2p3`, `1p_1`, `_1p1`, `1__2p1`, `1_p1`, `1.8_p1` | `_` | any | false |
| `1p1_2` | `_` | false | true |
| `1p1_` or `1p1_a` | `_` | false / true | false / true |
| `1p1.5` | none | false / true | false / true |

The input can be long (many thousands of characters); the work is a single left-to-right pass.

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `double-conversion/double-conversion.cc` (namespace `double_conversion`)
- **Target:** a file-local (`static`) function template. The line `template<class Iterator>` stands directly above the stub and stays in the file; **your answer must contain only the function as in the stub** (no template line, keep the signature exactly). It is instantiated with `Iterator = const char*` and `Iterator = const uc16*`.

## Includes available in this file

```
#include <climits>
#include <locale>
#include <cmath>
#include "double-conversion.h"
#include "bignum-dtoa.h"
#include "fast-dtoa.h"
#include "fixed-dtoa.h"
#include "ieee.h"
#include "strtod.h"
#include "utils.h"
```

## Types and constants

```
typedef uint16_t uc16;                                   // utils.h
// in class StringToDoubleConverter:
static const uc16 kNoSeparator = '\0';                   // "no separator" value for the separator parameter
```

## Helper functions defined earlier in the same file (you may call them)

```
// true if x is a white space character (ASCII white space and the Unicode white space code points)
static bool isWhitespace(int x);

// true if x is a digit of the given radix: '0'..'9' below the radix, and (for radix > 10) 'a'/'A' up to the radix
static bool isDigit(int x, int radix);

// Moves *it one position forward and returns true if the iterator is then equal to 'end' (the end was reached).
// If 'separator' is not kNoSeparator, a separator that directly follows a digit (digit test with 'base') and is
// itself followed by a digit (same base) is skipped too: after "1_2" the iterator is on the '2'.
// (If the character at *it is not a digit of the given base, only one position is advanced.)
template<class Iterator>
static bool Advance(Iterator* it, uc16 separator, int base, Iterator& end);

// Skips white space starting at *current. Returns true if a non-space character was found (*current is on it),
// false if the end was reached.
template<class Iterator>
static inline bool AdvanceToNonspace(Iterator* current, Iterator end);
```

## Caller (for orientation only)

```
// in StringToDoubleConverter::StringToIeee(), after the "0x" prefix was consumed (parse_as_hex_float is decided here):
if ((flags_ & ALLOW_HEX_FLOATS) && IsHexFloatString(current, end, separator_, allow_trailing_junk)) { parse_as_hex_float = true; }
// then RadixStringToIeee<4>(&current, end, sign, separator_, parse_as_hex_float, ...) reads the number.
```

=== STUB ===
```cpp
static bool IsHexFloatString(Iterator start,
                             Iterator end,
                             uc16 separator,
                             bool allow_trailing_junk) {
    // TODO: implement according to the specification
}
```
