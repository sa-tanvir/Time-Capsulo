# Functional specification: `Bignum::PlusCompare(a, b, c)`

## 1. Component overview

`Bignum` is the small arbitrary-precision, non-negative integer class used by the double-conversion library for exact decimal digit generation (at most 3584 significant bits). `PlusCompare` is a static member that compares the sum of two bignums with a third one: it answers "is `a + b` smaller than, equal to, or greater than `c`?". It is the primitive behind `PlusEqual`, `PlusLess` and `PlusLessEqual`, and the digit generators call it in their inner loops, so it must not change any of its arguments and should be cheap (cost proportional to the number of digits involved).

## 2. Functional requirements

1. Return the three-way comparison of the mathematical integer `a + b` against the mathematical integer `c`: `-1` if `a + b < c`, `0` if `a + b == c`, `+1` if `a + b > c`.
2. The result is exact. The comparison covers the complete values of the operands, including the low-order zero digits that are represented implicitly (see the instance state in the context).
3. The roles of `a` and `b` are symmetric: `PlusCompare(a, b, c) == PlusCompare(b, a, c)`.
4. The three arguments are `const` and must not be modified. The sum itself is never stored (the sum of two operands at the capacity limit may not fit into a `Bignum`); the function must also work in that situation.
5. A carry out of one digit into the next, including chains of carries over several digits, must be handled (for example `0xfffffff + 1 == 0x10000000` is a carry across a digit boundary in this representation).
6. Any of the three arguments may be zero.

## 3. Input specification

`a`, `b`, `c` are valid, normalised `Bignum` objects (see the context): the most significant stored digit is non-zero, and zero is the empty digit sequence with exponent 0. They may have different exponents and different digit counts and may refer to the same object (for example `PlusCompare(x, x, y)` compares `2x` with `y`).

## 4. Output specification

An `int` that is exactly `-1`, `0` or `+1`. No exceptions, no output parameters, no side effects.

## 5. Edge cases and constraints

| a | b | c | result |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | -1 |
| 1 | 0 | 0 | +1 |
| 1 | 1 | 2 | 0 |
| 1 | 1 | 3 | -1 |
| 1 | 1 | 1 | +1 |
| 0xfffffff | 1 | 0x10000000 | 0 |
| 0xfffffff | 1 | 0xfffffff | +1 |
| 0xfffffff | 1 | 0x10000001 | -1 |
| 0xffffffff | 0xffffffff | 0x1fffffffe | 0 |
| 1 << 84 (value) | 1 | (1 << 84) + 1 | 0 |
| 1 << 84 | 1 | 1 << 84 | +1 |

The comparison must be right when `a + b` has one more digit than the longer operand, when `c` is much shorter or much longer than both operands, and when the operands' implicit zero digits (exponents) differ widely.
