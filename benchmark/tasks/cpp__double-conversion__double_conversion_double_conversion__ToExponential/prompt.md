You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `DoubleToStringConverter::ToExponential(value, requested_digits, result_builder) const`

## 1. Component overview

`DoubleToStringConverter` formats `double` values as text according to a configuration that is fixed when the object is created (flags, the texts for infinity and NaN, the exponent character, and padding limits). `ToExponential` writes a number in exponential notation `d.ddde+x`, like JavaScript's `Number.prototype.toExponential`: one digit before the point, an optional fraction, the exponent character and a decimal exponent.

## 2. Functional requirements

1. **Special values**: if `value` is infinity or NaN, the result is whatever the converter's special-value handling produces (`HandleSpecialValues`, see the context): the infinity text (preceded by `-` for negative infinity) or the NaN text is appended and `true` is returned; if the corresponding symbol was configured as null nothing is appended and `false` is returned. This check comes first, before the digit count is validated.
2. **Digit count**: `requested_digits` is the number of digits after the point, or `-1` for "as many as needed". If `requested_digits < -1` or `requested_digits > kMaxExponentialDigits` (120), return `false` and append nothing.
3. **Digits**: for `requested_digits == -1` the digits are the shortest decimal digits that read back as `value` (the same digits `ToShortest` uses). Otherwise exactly `requested_digits + 1` significant digits are used: `value` rounded to that many significant digits (halfway cases rounded away from zero, as `DoubleToAscii` does in `PRECISION` mode); if the digit generator returns fewer digits than requested (trailing zeros dropped) the missing digits are filled with `'0'` so that exactly `requested_digits + 1` digits are written.
4. **Sign**: a `-` is written for negative values, including negative zero, unless the converter has the `UNIQUE_ZERO` flag and `value == 0.0` (then neither `0` nor `-0` gets a sign). Positive values and positive zero get no sign.
5. **Layout**: first digit, then (only if more than one digit) a `.` and the remaining digits, then the converter's exponent character, then the exponent: `-` followed by its absolute value for a negative exponent; for a non-negative exponent a `+` is written only when the converter has the `EMIT_POSITIVE_EXPONENT_SIGN` flag; the exponent is written in decimal without leading zeros (`0` for zero). The exponent is the decimal exponent of the first digit (value 12345.6 gives `4`), and zero has exponent 0. The layout is produced by the member `CreateExponentialRepresentation`, which you may call.
6. On success return `true` after appending the text to `result_builder` (the builder is not finalised). On a `false` return nothing has been appended.

## 3. Input specification

- `value`: any `double` including `+-0.0`, subnormal numbers, `+-infinity` and NaN.
- `requested_digits`: any `int`; the valid range is `-1 .. 120`.
- `result_builder`: non-null pointer to a `StringBuilder` with enough room for the result (about 130 characters at most).
- The converter's own settings are described in the context.

## 4. Output specification

`bool` and the appended characters.

## 5. Edge cases and constraints

The examples use a converter without flags, infinity text `Infinity`, NaN text `NaN` and exponent character `e` unless noted.

| value | requested_digits | flags | result |
|---|---|---|---|
| 3.0 | -1 | none | `3e0` |
| 12345.6789 | 2 | none | `1.23e4` |
| 12345.6789 | 2 | EMIT_POSITIVE_EXPONENT_SIGN | `1.23e+4` |
| 0.00001 | 3 | none | `1.000e-5` |
| -1.5 | 0 | none | `-2e0` |
| 1.25 | 1 | none | `1.3e0` |
| 1.35 | 1 | none | `1.4e0` |
| 9.99 | 1 | none | `1.0e1` |
| 123.456 | 5 | none | `1.23456e2` |
| 1e100 | -1 | EMIT_POSITIVE_EXPONENT_SIGN | `1e+100` |
| 0.0 | -1 | none | `0e0` |
| 0.0 | 3 | none | `0.000e0` |
| -0.0 | 2 | none | `-0.00e0` |
| -0.0 | 2 | UNIQUE_ZERO | `0.00e0` |
| +infinity | 2 | none | `Infinity` |
| -infinity | 2 | none | `-Infinity` |
| NaN | 2 | none | `NaN` |
| 5 | 121 | none | false, nothing appended |
| 5 | -2 | none | false, nothing appended |
| 5 | 120 | none | `5.` followed by 120 zeros and `e0` |
| infinity | any | null infinity symbol | false |

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `double-conversion/double-conversion.cc` (namespace `double_conversion`)
- **Target:** the out-of-class definition of the public `const` member function `DoubleToStringConverter::ToExponential`. Keep the signature exactly as in the stub. As a member it may use the private members and helpers below.

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
bool DoubleToStringConverter::ToExponential(
    double value,
    int requested_digits,
    StringBuilder* result_builder) const {
    // TODO: implement according to the specification
}
```
