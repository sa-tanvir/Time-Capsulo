# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `double-conversion/double-conversion.cc` (namespace `double_conversion`)
- **Target:** the out-of-class definition of the public `const` member function `DoubleToStringConverter::ToPrecision`. Keep the signature exactly as in the stub. As a member it may use the private members and helpers below.

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

## Instance state and constants (class `DoubleToStringConverter`, `double-conversion.h`)

```
class DoubleToStringConverter {
 public:
  static const int kMaxFixedDigitsBeforePoint = 60;
  static const int kMaxFixedDigitsAfterPoint = 60;
  static const int kMaxExponentialDigits = 120;
  static const int kMinPrecisionDigits = 1;
  static const int kMaxPrecisionDigits = 120;
  enum Flags { NO_FLAGS = 0, EMIT_POSITIVE_EXPONENT_SIGN = 1, EMIT_TRAILING_DECIMAL_POINT = 2,
               EMIT_TRAILING_ZERO_AFTER_POINT = 4, UNIQUE_ZERO = 8 };
  enum DtoaMode { SHORTEST, SHORTEST_SINGLE, FIXED, PRECISION };
  static const int kBase10MaximalLength = 17;

  // Generates the decimal digits of v in the given mode into buffer (NOT NUL-terminated), sets *sign (true for negative
  // values and -0.0), *length (number of digits) and *point so that the value is 0.DIGITS * 10^point, i.e. the decimal
  // point is after the first 'point' digits (value 123 gives digits "123", point 3; 0.0123 gives "123", point -1).
  //   SHORTEST: the least number of digits that read back as v (requested_digits is ignored).
  //   PRECISION: at most requested_digits significant digits (the first is not '0'), rounded, halfway cases away from zero;
  //     it may return fewer digits when trailing zeros are dropped, the caller then fills with '0'.
  //   For v == 0 the digits are "0" with point 1. v must be finite.
  // buffer_length must be large enough for the digits plus a NUL character.
  static void DoubleToAscii(double v, DtoaMode mode, int requested_digits, char* buffer, int buffer_length,
                            bool* sign, int* length, int* point);

 private:
  // If value is +-infinity: appends "-" (for -infinity) and the infinity text, returns true; returns false (nothing appended)
  // when the infinity text is null. If value is NaN: appends the NaN text and returns true, false when it is null.
  // For any other value returns false and appends nothing.
  bool HandleSpecialValues(double value, StringBuilder* result_builder) const;

  // Appends d[.ddd]<exponent_character_>[-|+]<exponent>: decimal_digits[0], then (if length != 1) '.' and the other digits,
  // then the exponent character, then '-' for a negative exponent or '+' for a non-negative one when
  // EMIT_POSITIVE_EXPONENT_SIGN is set, then the absolute value of the exponent in decimal without leading zeros ("0" for 0).
  void CreateExponentialRepresentation(const char* decimal_digits, int length, int exponent, StringBuilder* result_builder) const;

  // Appends the digits in plain notation with exactly digits_after_point digits after the decimal point, padded with zeros:
  //   decimal_point <= 0: "0." + (-decimal_point zeros) + digits + zero padding  (just "0" when digits_after_point == 0)
  //   decimal_point >= length: digits + (decimal_point - length) zeros, then "." and digits_after_point zeros (if > 0)
  //   otherwise: the first decimal_point digits, '.', the rest, zero padding.
  // When digits_after_point == 0 it appends '.' if EMIT_TRAILING_DECIMAL_POINT is set, and then '0' if
  // EMIT_TRAILING_ZERO_AFTER_POINT is set.
  void CreateDecimalRepresentation(const char* decimal_digits, int length, int decimal_point, int digits_after_point,
                                   StringBuilder* result_builder) const;

  const int flags_;                                       // OR of Flags
  const char* const infinity_symbol_;                     // may be NULL
  const char* const nan_symbol_;                          // may be NULL
  const char exponent_character_;
  const int decimal_in_shortest_low_;                     // (used by ToShortest only)
  const int decimal_in_shortest_high_;                    // (used by ToShortest only)
  const int max_leading_padding_zeroes_in_precision_mode_;   // used by ToPrecision
  const int max_trailing_padding_zeroes_in_precision_mode_;  // used by ToPrecision
};

template <typename T> static T Max(T a, T b);             // utils.h
class StringBuilder {                                     // utils.h: AddCharacter(char c), AddString(const char*),
};                                                        //   AddSubstring(const char*, int n), AddPadding(char c, int count)
class Double { public: explicit Double(double d); bool IsSpecial() const;   // true for infinity and NaN   (ieee.h)
               bool IsInfinite() const; bool IsNan() const; };
```

## Callers (for orientation only)

```
// public API, e.g. in the tests:  converter.ToExponential(123.456, 5, &builder);   converter.ToPrecision(123456, 3, &builder);
```
Related members defined in the same file: `ToShortestIeeeNumber`, `ToFixed`, `ToExponential`, `ToPrecision`, `EcmaScriptConverter`.
