# Functional specification: `GenerateShortestDigits(numerator, denominator, delta_minus, delta_plus, is_even, buffer, length)`

## 1. Component overview

This is the last step of the exact ("bignum") shortest double-to-string conversion in the double-conversion library. A positive floating-point number `v` has been scaled to a ratio `numerator / denominator` (a real number `x` with `1 <= x < 10`, so `v = x * 10^k` for some `k`), together with two rounding margins `delta_minus / denominator` and `delta_plus / denominator` that describe how far the decimal result may lie below and above `x` and still read back as `v`. The function produces the decimal digits of `x`, from the most significant one, and stops at the first digit sequence that lies inside the margins, rounding the last digit correctly. The result is the shortest digit string that identifies `v`.

## 2. Functional requirements

All numbers below are exact (the arguments are `Bignum` objects). Digits are produced one at a time. After producing the digit number `j` (the first digit is the one in front of the decimal point), let `R` be the part of the value not yet represented by the digits written so far, scaled so that one unit in the last written digit equals `denominator`; let `M-` and `M+` be the two margins scaled the same way, and let `D` be the denominator.

1. The `j`-th digit is the integer quotient `R / D` (with `R` starting as `numerator` for `j = 1`); the remainder replaces `R`. The digit is appended to `buffer` as an ASCII character `'0'..'9'`.
2. After each digit decide whether the digits written so far may be accepted:
   - "round down is allowed" if `R <= M-` (when `is_even` is true) or `R < M-` (when `is_even` is false);
   - "round up is allowed" if `R + M+ >= D` (when `is_even` is true) or `R + M+ > D` (when `is_even` is false).
3. If neither is allowed, the remainder and both margins are multiplied by 10 and the next digit is produced.
4. If only "round down" is allowed, stop and keep the digits as they are.
5. If only "round up" is allowed, stop after adding 1 to the last written digit.
6. If both are allowed, compare `2 * R` with `D`: if it is smaller keep the digits; if it is larger add 1 to the last digit; if it is equal (an exact tie) keep the last digit when it is even and add 1 to it when it is odd.
7. On return `*length` is the number of digits written (at least 1). The digits are not NUL-terminated by this function.
8. The four bignum arguments are working storage: their values after the call are unspecified (callers do not use them again).

## 3. Input specification

- `numerator`, `denominator`, `delta_minus`, `delta_plus`: pointers to valid, normalised `Bignum` objects, all non-null and distinct. `denominator > 0`. `numerator < 10 * denominator` and `(numerator + delta_plus) / denominator` is in `[1, 10)`, so that no digit above 9 and no leading zero is produced and rounding up never has to carry out of a `'9'` (the last digit is never `'9'` when it is incremented).
- `is_even`: `bool`, true when the original floating-point significand is even (the interval boundaries are then included).
- `buffer`: `Vector<char>` with room for all digits (17 digits are enough for a double, 9 for a float; the driver supplies 32 characters). `length`: non-null `int*`.

## 4. Output specification

The digits in `buffer[0 .. *length)` and `*length`.

## 5. Edge cases and constraints

Examples (`numerator / denominator`, margins, `is_even` -> digits):

| numerator | denominator | delta_minus | delta_plus | is_even | digits |
|---|---|---|---|---|---|
| 10 | 3 | 1 | 1 | true | `3` |
| 10 | 3 | 1 | 1 | false | `33` |
| 3 | 2 | 1 | 1 | true | `2` (tie after the first digit, 1 is odd, so it is rounded up) |
| 3 | 2 | 1 | 1 | false | `15` |
| 1234 | 1000 | 1 | 1 | true | `1234` |
| 1234 | 1000 | 5 | 5 | true | `123` |
| 1234 | 1000 | 50 | 50 | true | `12` |
| 1234 | 1000 | 6 | 40 | true | `123` |
| 1234 | 1000 | 40 | 6 | true | `12` |
| 25 | 10 | 5 | 5 | true | `2` |
| 35 | 10 | 5 | 5 | true | `4` |
| 35 | 10 | 5 | 5 | false | `35` |
| 5 | 2 | 1 | 1 | false | `25` |

The numbers can be very large (up to the capacity of a `Bignum`, thousands of bits, when the original value is near the ends of the double range); the loop runs at most 17 times for doubles.
