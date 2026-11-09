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
