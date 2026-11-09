You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `RadixStringToIeee<radix_log_2>(current, end, sign, separator, parse_as_hex_float, allow_trailing_junk, junk_string_value, read_as_double, result_is_junk)`

## 1. Component overview

`StringToDoubleConverter` in the double-conversion library reads numbers with a prefix: `0x` (hexadecimal, optionally a hex float such as `1.8p3`), and `0` followed by octal digits. After the prefix has been consumed, this function template reads the digits of a number whose radix is a power of two, `radix = 2^radix_log_2` (the template argument, 1 to 5: binary, base 4, octal, hexadecimal, base 32), and returns it as a `double`, correctly rounded to the precision of the target type (53 bits for `double`, 24 bits for `float`).

## 2. Functional requirements

Notation: `*current` is the read position (an iterator that is advanced), `end` the end of the text. Digits are `0-9` and the letters `a-z` / `A-Z` (either case) with value below the radix; for example radix 16 accepts `0-9a-fA-F`.

1. **Sign**: the result is the unsigned value, negated when `sign` is true. A zero result is `-0.0` when `sign` is true and `+0.0` otherwise.
2. **Leading zeros** are skipped. If the text ends while skipping zeros (the text consists only of zeros) the function stops, sets `*result_is_junk = false`, leaves `*current == end` and returns the signed zero.
3. **Digits** are read from the position after the leading zeros. The value is the integer formed by all digits read. Separators: if `separator` is not `StringToDoubleConverter::kNoSeparator` (code 0), one separator that is directly between two digits is skipped (the helper `Advance` in the context moves the position that way and reports the end of the text; use it for every step). Any other occurrence of the separator is an ordinary non-digit character.
4. **End of the digits**: the digits end at the end of the text or at the first character that is not a digit. In the plain (non-hex-float) mode that character is handled as follows:
   - if `allow_trailing_junk` is true, reading simply stops there and `*current` stays on that character (even if it is white space);
   - otherwise the remaining text may only be white space: the white space is consumed (`*current` is then `end`) and the number is accepted; if a non-white-space character follows, the function returns `junk_string_value`, sets `*result_is_junk = true`, and `*current` is on that offending (non-white-space) character.
5. **Rounding**: if the digits read need more significant bits than the target precision (53 for `read_as_double`, otherwise 24), the value is rounded to the nearest number with that many significant bits, with ties going to the even result, taking into account all remaining digits that belong to the number (a non-zero digit anywhere after the cut makes an exact-looking tie round up). Reading continues over the remaining digits, so the end of the digits and the junk rules of item 4 apply in the same way (the junk check happens after those digits). Rounding up may carry into a new bit, which is handled. Results that exceed the largest double are `+-infinity`.
6. **Hex floats**: if `parse_as_hex_float` is true (only used with `radix_log_2 == 4`; the caller guarantees the text from `*current` is a valid hex float as `IsHexFloatString(*current, end, separator, allow_trailing_junk)` would accept it: hex digits with at most one `.`, then `p` or `P`, an optional sign, decimal digits), the mantissa digits may contain one `.`; the value is `mantissa * 2^exponent` where the mantissa includes its fractional hex digits (each digit after the point scales it by 1/16) and the exponent is the signed decimal number after the `p`. Rounding of long mantissas follows item 5; any further digits after the cut (including ones after the point) are included in the rounding decision and the point is stepped over. After the exponent digits reading ends: the function does **not** look at what follows (no trailing-white-space consumption and no junk check; `*current` is directly after the last exponent digit, or after the exponent digits including any skipped separators), and `*result_is_junk` is false. The exponent digits can be very many (leading zeros) or very large (such as `p+99999`); this must not overflow, a huge positive exponent gives `+-infinity`. Results below the normal double range are not used by callers and are outside this contract. A hex float whose mantissa is zero (`0p5`, `0.0p5`) gives the signed zero.
7. **Result flags**: `*result_is_junk` is set to true exactly when `junk_string_value` is returned (item 4), and to false in every other case.
8. **Returned position**: on return `*current` is the position of the first character that was not consumed: `end` when everything was consumed, and as described in items 2, 4 and 6 otherwise.
9. The function does not read any character at or after `end`.
10. `read_as_double == false` only changes the precision used for rounding in item 5; the value is still returned as a `double` (which then holds a number with at most 24 significant bits).

## 3. Input specification

- `radix_log_2`: template argument, `1 <= radix_log_2 <= 5`; `Iterator`: `const char*` or `const uc16*` (`uc16` is `uint16_t`).
- `current`: non-null `Iterator*`, `*current != end` (the text is not empty). `end`: the end iterator.
- `sign`, `parse_as_hex_float`, `allow_trailing_junk`, `read_as_double`: `bool`; `separator`: `uc16` (0 = none); `junk_string_value`: `double`; `result_is_junk`: non-null `bool*`.
- The first character of the text is a digit of the radix, or (in hex float mode) a digit or `.`.

## 4. Output specification

The returned `double` as described (value or `junk_string_value`), the advanced `*current`, and `*result_is_junk`. No exceptions.

## 5. Edge cases and constraints

All examples use the default `separator` 0 unless noted, `read_as_double` true, `allow_trailing_junk` false, `junk_string_value` 777.0.

| radix_log_2 | text | notes | result, `consumed`, `is_junk` |
|---|---|---|---|
| 4 | `ff` | | 255, 2, false |
| 4 | `0`, sign true | | -0.0, 1, false |
| 4 | `000`, sign true | | -0.0, 3, false |
| 1 | `101` | | 5, 3, false |
| 3 | `777` | | 511, 3, false |
| 5 | `vV` | | 1023, 2, false |
| 4 | `20000000000001` | 2^53 + 1, a tie | 9007199254740992 (even), 14, false |
| 4 | `20000000000003` | 2^53 + 3, a tie | 9007199254740996, 14, false |
| 4 | `20000000000002` | exact | 9007199254740994, 14, false |
| 4 | `200000000000011` | 2^57 + 17, above the tie (step 32) | 144115188075855904, 15, false |
| 4 | `1000001`, `read_as_double` false | 24 bits, a tie | 16777216, 7, false |
| 4 | `1000003`, `read_as_double` false | | 16777220, 7, false |
| 4 | `ff z` | | 777, 3, true |
| 4 | `ff z`, junk allowed | | 255, 2, false |
| 4 | `ff  ` | trailing spaces | 255, 4, false |
| 4 | `ff  `, junk allowed | | 255, 2, false |
| 4 | `fzf` | | 777, 1, true |
| 4 | `fzf`, junk allowed | | 15, 1, false |
| 4 | `0z` | | 777, 1, true |
| 4 | `0z`, junk allowed | | 0, 1, false |
| 4 | `1_f`, separator `_` | | 31, 3, false |
| 4 | `1__f`, separator `_`, junk allowed | | 1, 1, false |
| 4 | `1_`, separator `_`, junk allowed | | 1, 1, false |
| 4 | `1p0`, hex float | | 1, 3, false |
| 4 | `1p4`, hex float | | 16, 3, false |
| 4 | `1.8p1`, hex float | | 3, 5, false |
| 4 | `1.8p1`, hex float, sign true | | -3, 5, false |
| 4 | `0p5`, hex float, sign true | | -0.0, 3, false |
| 4 | `1p-1`, hex float | | 0.5, 4, false |
| 4 | `1p+99999`, hex float | | infinity, 8, false |
| 4 | `1p1 `, hex float | trailing space is not consumed | 2, 3, false |
| 4 | `.8p0`, hex float | | 0.5, 4, false |
| 4 | `1.p3`, hex float | | 8, 4, false |
| 4 | `1.fffffffffffff8p0`, hex float | tie, odd, rounds up | 2, 18, false |
| 4 | `1.0000000000000800000p0`, hex float | exact tie, even | 1, 23, false |
| 4 | `1.0000000000000800001p0`, hex float | above the tie | 1.0000000000000002, 23, false |
| 4 | `1.8p000001`, hex float | | 3, 10, false |
| 3 | `12345670123456701234567` | 23 octal digits | 96374504495306326016, 23, false |
| 1 | `1`, 52 times `0`, then `11` (2^54 + 3) | rounds up | 18014398509481988, 55, false |

The text can be long: leading zeros, many fraction digits, long exponents and trailing white space of tens of thousands of characters occur; reading is linear in the text length.

=== CONTEXT ===
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

=== STUB ===
```cpp
static double RadixStringToIeee(Iterator* current,
                                Iterator end,
                                bool sign,
                                uc16 separator,
                                bool parse_as_hex_float,
                                bool allow_trailing_junk,
                                double junk_string_value,
                                bool read_as_double,
                                bool* result_is_junk) {
    // TODO: implement according to the specification
}
```
