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
