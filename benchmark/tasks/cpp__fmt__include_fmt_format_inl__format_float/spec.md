# Functional specification: `format_float(value, precision, specs, buf)`

## 1. Component overview

Converts a non-negative floating-point number to decimal "digits and exponent" form for fmt's floating-point formatting. The digits are stored in `buf` (ASCII, not NUL-terminated, `buf.size()` = number of digits) and the function returns a decimal exponent `e`, so that the number is approximately `digits * 10^e` (the digit string read as an integer). A later stage places the decimal point, signs, padding and exponent text, so the digit conventions below must be followed exactly.

## 2. Functional requirements

`value >= 0` (a negative value is never passed), finite. `specs.format` is `general`, `exp` or `fixed`. `buf` is empty on entry with capacity of at least a few hundred characters. `precision` has the meaning given by the caller: for `fixed` it is the number of digits after the decimal point (>= 0); for `general` and `exp` it is the number of significant digits (>= 1); `-1` means no precision (shortest representation, see rule 5).

1. **Zero.** If `value == 0`: if `precision <= 0` or the format is not `fixed`, the buffer becomes the single digit `0` and the function returns 0; otherwise (`fixed`, `precision > 0`) the buffer becomes `precision` characters `'0'` and the function returns `-precision`.
2. **Without the fast generator.** If `specs.use_grisu` is false, the result is exactly what `snprintf_float(value, precision, specs, buf)` produces (digits in `buf` and its return value).
3. **High precision.** If `precision > 17` the result is also exactly that of `snprintf_float(value, precision, specs, buf)`.
4. **Fixed number of digits (`0 <= precision <= 17`, `use_grisu` set).**
   - `fixed`: let `q` be `value * 10^precision` rounded to the nearest integer, ties to even (exact decimal value of the binary number, correct rounding). The buffer holds the decimal digits of `q` without leading zeros and the function returns `-precision`. If `q` is zero the buffer holds the single digit `0` or is empty (callers print zero in both cases) and the returned exponent is `-precision`. (Exactness is only guaranteed while the number of integer digits plus `precision` does not exceed 17.)
   - `general` / `exp` (`precision >= 1`): the buffer holds the `precision` most significant decimal digits of `value`, correctly rounded (nearest, ties to even on the exact binary value), **with trailing zeros removed**; every removed zero increases the returned exponent by one. Example: `1500.0` with precision 6 gives digits `15` and returns 2; `100.0` with precision 3 gives `1` and 2; `0.001` with precision 3 gives `1` and -3; `123.456` with precision 3 gives `123` and 0; `99.99` with precision 3 gives `1` and 2 (rounds up to 100).
5. **Shortest representation (`precision == -1`, `use_grisu` set).** The buffer holds the shortest decimal digit string that, read back as a number of the same type, gives exactly `value` (if several of the shortest length exist, the one closest to `value`), without trailing zeros; the function returns the exponent such that `digits * 10^e` is that decimal. If `specs.binary32` is set the value is a float promoted to double and "read back" is as a float. Examples: `0.1` gives `1`, -1; `100.0` gives `1`, 2; `123.456` gives `123456`, -3; `5e-324` gives `5`, -324; `1e22` gives `1`, 22; `0.99960000000000004` gives `9996`, -4.

When rule 2 or 3 applies the digit conventions of `snprintf_float` (including its handling of `fixed`, where leading zeros of the integer part are kept) are used, so those results differ in form from rule 4; both forms are accepted by the later stage.

## 3. Input specification

- `T` is `double` or `long double`; `long double` is always called with `use_grisu` false.
- `value` finite, `>= 0`. `precision` as above; `fixed` is never called with `-1`, `general`/`exp` are never called with `0`.
- `specs.use_grisu`, `specs.binary32` as described; the `trailing_zeros`, `upper`, `sign`, `locale`, `percent` members do not affect the digits (except through `snprintf_float` where it documents them).

## 4. Output specification

Returns the decimal exponent `e` and leaves the digits in `buf` as described. No exceptions. Behaviour for precondition violations is unspecified.

## 5. Edge cases and constraints

- Denormals (`5e-324`) and the largest doubles (`1.7976931348623157e308`) are valid inputs: shortest gives `17976931348623157` and 292.
- Rounding must be correct to the last digit: `fixed` with precision 2: `1.005` (really 1.00499999999999989...) gives `100`, -2; `0.5` with precision 0 gives `0` (tie to even); `1.5` gives `2`; `2.5` gives `2`.
- `fixed`, `precision` 2, `0.001` gives a zero result (`0` or empty) with exponent `-2`.
- Trailing zeros are only stripped for `general`/`exp` (rule 4) and in rule 5; `fixed` keeps all `integer digits + precision` digits (`100.0` with precision 2 gives `10000`, -2).
