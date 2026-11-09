# Functional specification: `Bignum::AssignPowerUInt16(base, power_exponent)`

## 1. Component overview

`Bignum` is the fixed-capacity, non-negative arbitrary-precision integer class of the double-conversion library (at most 3584 significant bits, i.e. 128 stored 28-bit digits). `AssignPowerUInt16` overwrites the object with the integer power `base ^ power_exponent`. It is used to create powers of ten (and occasionally other small bases) when the digit generators set up their exact numerators and denominators, so it is called with bases such as 10 and with exponents up to several hundred.

## 2. Functional requirements

1. Afterwards the object's value is exactly `base` raised to the power `power_exponent` (an exact integer, no rounding). Any value the object held before the call is discarded.
2. `power_exponent == 0` yields the value 1 for every base. `base == 1` yields 1 for every exponent.
3. The object must be left in a valid normalised state (see the context): the result must be usable by every other `Bignum` operation (`Compare`, `Square`, `MultiplyByUInt32`, `ShiftLeft`, `ToHexString`, ... ) exactly as if it had been created by `AssignUInt64`, `AssignHexString` or any other public assignment.
4. The base is an unsigned 16-bit value and may be even; powers of two contained in the base (for example the 2 in `10`) are allowed to be handled however you like as long as the value is exact.
5. The function does not return a value and has no other effect on the object.

## 3. Input specification

- `base`: `uint16_t`, `1 <= base <= 65535`. A base of 0 is not allowed.
- `power_exponent`: `int`, `power_exponent >= 0`.
- The caller guarantees that the result fits into the capacity of a `Bignum`: let `odd` be `base` with all factors of two removed; then `bit_length(odd) * power_exponent` is at most 3300, and the total bit length of the result is at most 3500. (`base == 1` is allowed with any exponent.) For results of this size no capacity check is required.

## 4. Output specification

The object itself holds the result. It is observable through the public interface, for example `ToHexString` (lower-case hexadecimal digits, no leading zeros, `"0"` is never produced here) and `Compare`.

## 5. Edge cases and constraints

| base | power_exponent | value (hexadecimal) |
|---|---|---|
| 10 | 0 | 1 |
| 10 | 1 | a |
| 10 | 2 | 64 |
| 1 | 7 | 1 |
| 2 | 10 | 400 |
| 3 | 5 | f3 |
| 16 | 15 | 1 followed by 15 zeros (2^60) |
| 65535 | 1 | ffff |
| 65535 | 2 | fffe0001 |
| 65535 | 4 | fffc0005fffc0001 |

The function is called many times (the exponent can be several hundred and the result can be thousands of bits long), so efficiency matters.
