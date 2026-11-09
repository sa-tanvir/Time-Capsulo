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
