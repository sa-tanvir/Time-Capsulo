# Functional specification

## 1. Component overview

`Fraction.greatestCommonDivisor(u, v)` returns the greatest common divisor of two `int` values as a non-negative `int`. It must work for the entire `int` range, including `Integer.MIN_VALUE`, whose absolute value does not fit in an `int`.

## 2. Functional requirements

1. If either `u` or `v` is `0`:
   - if either argument is `Integer.MIN_VALUE`, throw `ArithmeticException` with the message `overflow: gcd is 2^31` (the true gcd, 2^31, does not fit);
   - otherwise return `|u| + |v|` (so `gcd(0, 0) = 0` and `gcd(0, x) = |x|`).
2. Otherwise, if either `|u|` or `|v|` equals `1`, return `1`.
3. Otherwise return the mathematical gcd of `|u|` and `|v|`, where the sign of the arguments is ignored (`gcd(-12, 18) = 6`, `gcd(12, -18) = 6`, `gcd(-12, -18) = 6`). The result is always positive in this case.
4. If the true gcd is `2^31` (which happens only when both arguments are `Integer.MIN_VALUE`), throw `ArithmeticException` with the message `overflow: gcd is 2^31`. Every other pair with a nonzero argument has a gcd that fits in an `int`; for example `gcd(Integer.MIN_VALUE, 2^30) = 2^30` and `gcd(Integer.MIN_VALUE, 6) = 2`.
5. The computation must never overflow or produce a wrong result for any `int` pair. Performance is measured: the method is called many times on large operands.

## 3. Input specification

`u`, `v`: any `int` values.

## 4. Output specification

A non-negative `int` (zero only for `(0, 0)`). Examples: `(0, 0)` -> 0; `(0, -5)` -> 5; `(-5, 0)` -> 5; `(1, 99)` -> 1; `(-1, 99)` -> 1; `(12, 18)` -> 6; `(-12, 18)` -> 6; `(17, 5)` -> 1; `(1024, 96)` -> 32; `(Integer.MIN_VALUE, 0)` -> exception; `(Integer.MIN_VALUE, Integer.MIN_VALUE)` -> exception; `(Integer.MIN_VALUE, 1)` -> 1; `(Integer.MAX_VALUE, Integer.MIN_VALUE)` -> 1.

## 5. Edge cases and constraints

- Symmetric in `u` and `v`.
- Pure function, thread-safe; no argument validation other than the overflow cases above.
- Exception type and message are tested.
