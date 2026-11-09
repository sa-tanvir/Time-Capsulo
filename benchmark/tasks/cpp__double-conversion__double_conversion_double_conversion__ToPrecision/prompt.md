You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `DoubleToStringConverter::ToPrecision(value, precision, result_builder) const`

## 1. Component overview

`DoubleToStringConverter` formats `double` values as text according to a configuration fixed when the object is created (flags, texts for infinity and NaN, the exponent character, and padding limits). `ToPrecision` writes a number with a given number of significant digits, like JavaScript's `Number.prototype.toPrecision`: either in plain decimal notation or, when that would need too many padding zeros, in exponential notation.

## 2. Functional requirements

1. **Special values**: if `value` is infinity or NaN, the result is what the converter's special-value handling produces (`HandleSpecialValues`, see the context): the infinity text (with a leading `-` for negative infinity) or the NaN text is appended and `true` is returned; with a null symbol nothing is appended and `false` is returned. This check comes first.
2. **Precision range**: `precision` must be between `kMinPrecisionDigits` (1) and `kMaxPrecisionDigits` (120) inclusive; otherwise return `false` and append nothing.
3. **Digits**: `value` is rounded to `precision` significant digits (halfway cases away from zero), as `DoubleToAscii` does in `PRECISION` mode. The digit generator may return fewer digits than `precision` (trailing zeros dropped). Let `decimal_point` be its position of the decimal point (value 123.0 has digits `123` and `decimal_point` 3, value 0.0123 has digits `123` and `decimal_point` -1, zero has digit `0` and `decimal_point` 1).
4. **Sign**: a `-` is written for negative values, including negative zero, unless the converter has the `UNIQUE_ZERO` flag and `value == 0.0` (then there is no sign).
5. **Choice of notation**. Let `extra_zero` be 1 if the converter has the `EMIT_TRAILING_ZERO_AFTER_POINT` flag and 0 otherwise. Exponential notation is used when
   - `-decimal_point + 1 > max_leading_padding_zeroes_in_precision_mode_`, or
   - `decimal_point - precision + extra_zero > max_trailing_padding_zeroes_in_precision_mode_`;

   otherwise plain notation is used.
6. **Exponential notation**: the digits are first padded with `'0'` to exactly `precision` digits, then written by `CreateExponentialRepresentation` with exponent `decimal_point - 1` (first digit, `.` and the rest if there is more than one digit, the exponent character, the exponent with `-` or optional `+` as configured, see the context).
7. **Plain notation**: the digits are written by `CreateDecimalRepresentation` (the digits as returned, not padded) with `decimal_point` and with `max(0, precision - decimal_point)` digits after the point, so that the total number of significant digits shown is `precision` (zeros are added where needed; trailing `.` / `.0` are added by that helper according to the flags when no digits follow the point).
8. On success return `true` after appending the text to `result_builder` (not finalised). Nothing is appended when `false` is returned.

## 3. Input specification

- `value`: any `double`, including `+-0.0`, subnormals, `+-infinity`, NaN.
- `precision`: any `int`; valid range `1 .. 120`.
- `result_builder`: non-null `StringBuilder*` with room for the result (at most about 140 characters).
- Converter settings as in the context; `max_leading_padding_zeroes_in_precision_mode_` and `max_trailing_padding_zeroes_in_precision_mode_` are non-negative small integers.

## 4. Output specification

`bool` and the appended characters.

## 5. Edge cases and constraints

Examples (leading limit 6, trailing limit 0, no flags, infinity text `Infinity`, NaN text `NaN`, exponent character `e` unless a column says otherwise):

| value | precision | leading / trailing limit, flags | result |
|---|---|---|---|
| 123456 | 3 | 6 / 0 | `1.23e5` |
| 123456 | 3 | 6 / 12 | `123000` |
| 123456 | 6 | 6 / 0 | `123456` |
| 123456 | 7 | 6 / 0 | `123456.0` |
| 0.000123 | 3 | 6 / 0 | `0.000123` |
| 1.23e-5 | 3 | 6 / 0 | `0.0000123` |
| 1 | 1 | 6 / 0 | `1` |
| 1 | 5 | 6 / 0 | `1.0000` |
| 1 | 1 | 6 / 0, EMIT_TRAILING_DECIMAL_POINT | `1.` |
| 1 | 1 | 6 / 0, EMIT_TRAILING_DECIMAL_POINT and EMIT_TRAILING_ZERO_AFTER_POINT | `1e0` |
| 123456 | 3 | 6 / 3, both of those flags | `1.23e5` |
| 0.0 | 5 | 6 / 0 | `0.0000` |
| -0.0 | 3 | 6 / 0 | `-0.00` |
| -0.0 | 3 | 6 / 0, UNIQUE_ZERO | `0.00` |
| 99.99 | 3 | 6 / 0 | `100` |
| 0.5 | 1 | 6 / 0 | `0.5` |
| 1e21 | 3 | 6 / 30 | `1000000000000000000000` |
| 255 | 2 | 6 / 5 | `260` |
| 0.5 | 0 | any | false, nothing appended |
| 5 | 121 | any | false, nothing appended |
| infinity / NaN | any | `Infinity` / `NaN` | `Infinity` (`-Infinity` for negative) / `NaN` |

=== CONTEXT ===
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

=== STUB ===
```cpp
bool DoubleToStringConverter::ToPrecision(double value,
                                          int precision,
                                          StringBuilder* result_builder) const {
    // TODO: implement according to the specification
}
```
