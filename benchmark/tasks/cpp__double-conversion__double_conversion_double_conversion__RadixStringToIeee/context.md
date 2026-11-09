# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `double-conversion/double-conversion.cc` (namespace `double_conversion`)
- **Target:** a file-local (`static`) function template. The line `template <int radix_log_2, class Iterator>` stands directly above the stub and stays in the file; **your answer must contain only the function as in the stub** (no template line, keep the signature exactly). It is instantiated with `radix_log_2` = 1..5 and `Iterator` = `const char*` or `const uc16*`.

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
typedef uint16_t uc16;                                    // utils.h
static const uc16 kNoSeparator = '\0';                    // StringToDoubleConverter::kNoSeparator

// ieee.h
class Double {                                            // IEEE double view
 public:
  static const int kSignificandSize = 53;                 // Double::kSignificandSize
  static const int kMaxExponent = 0x7FF - 0x3FF - 52;     // Double::kMaxExponent (= 972)
  explicit Double(DiyFp d);                               // build from a DiyFp (significand f, binary exponent e); value() = f * 2^e;
  double value() const;                                   // too large exponents give infinity
};
class Single { public: static const int kSignificandSize = 24; };   // Single::kSignificandSize
class DiyFp {                                             // diy-fp.h: a 64-bit significand and an int exponent
 public:
  DiyFp(uint64_t significand, int exponent);
};
```
(`abs` from `<cstdlib>` is available.)

## Helper functions defined earlier in the same file (you may call them)

```
static bool isWhitespace(int x);                          // ASCII and Unicode white space
static bool isDigit(int x, int radix);                    // '0'..'9' below the radix; letters a/A.. up to the radix (radix > 10)
static double SignedZero(bool sign);                      // sign ? -0.0 : 0.0
static bool IsDecimalDigitForRadix(int c, int radix);     // '0' <= c <= '9' and (c - '0') < radix
static bool IsCharacterDigitForRadix(int c, int radix, char a_character);  // radix > 10 and c in [a_character, a_character + radix - 10);
                                                          //   a_character is 'a' or 'A'

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

// Validity test for hex floats (see its own task); returns true for text like "1.8p3" ("0x" already consumed).
template<class Iterator>
static bool IsHexFloatString(Iterator start, Iterator end, uc16 separator, bool allow_trailing_junk);
```

## Caller (for orientation only)

```
// in StringToDoubleConverter::StringToIeee(), after a "0x" / "0" prefix:
return RadixStringToIeee<4>(&current, end, sign, separator_, parse_as_hex_float, allow_trailing_junk, junk_string_value_, read_as_double, &result_is_junk);
// (radix_log_2 is 3 for octal, 4 for hexadecimal; the caller then casts to float when it reads a float)
```
