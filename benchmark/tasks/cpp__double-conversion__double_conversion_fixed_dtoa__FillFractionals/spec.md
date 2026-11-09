# Functional specification: `FillFractionals(fractionals, exponent, fractional_count, buffer, length, decimal_point)`

## 1. Component overview

Part of the fixed-notation double-to-string conversion (`FastFixedDtoa`) of the double-conversion library. The integer part of a number has already been written as decimal digits into `buffer`; this function appends the decimal digits of the fractional part, at most `fractional_count` of them, and rounds the result (round half up). The fractional part is given as a binary fixed-point number.

## 2. Functional requirements

1. The fractional value is `f = fractionals * 2^exponent` (with `0 <= f < 1`): `fractionals` is an integer, `exponent` is in `[-128, 0]`, and the binary point is `-exponent` bits to the left of the lowest bit.
2. Append decimal digits of `f` to `buffer`, starting at position `*length` (the buffer may already hold `*length` digits written by the caller), most significant digit first: the first appended digit is the tenths digit, the next the hundredths digit, and so on. Leading zero digits of the fraction are appended like any other digit (for `f = 0.0625` the digits are `0`, `6`, `2`, `5`).
3. At most `fractional_count` digits are appended. Digit generation also stops early as soon as the remaining fraction is exactly zero, so no trailing zero digits are produced after the last non-zero digit (a fraction that is already zero, for example `fractionals == 0`, appends nothing).
4. `*length` is increased by the number of appended digits.
5. Rounding: when digit generation has stopped and the remainder (the part of `f` not represented by the appended digits) is at least one half of a unit of the last appended digit, the written number is rounded up by one unit in the last place, i.e. the last digit in the buffer is incremented. If it becomes `'9' + 1` it is turned into `'0'` and the carry moves to the previous digit, continuing through digits that the caller had written before the call. If the carry leaves the first digit of the buffer, that digit becomes `'1'`, all digits after it are `'0'` and `*decimal_point` is increased by one.
6. If the buffer holds no digits at all (`*length == 0` when rounding up is required, so the fraction is not zero but smaller than the first digit), rounding up writes the single digit `'1'`, sets `*length` to 1 and sets `*decimal_point` to 1.
7. `*decimal_point` is otherwise left untouched. The buffer is not NUL-terminated by this function.
8. The remainder is judged exactly (the conversion is exact for every allowed input, including `exponent` below `-64` where more than 64 bits are involved).

## 3. Input specification

- `fractionals`: `uint64_t`, `fractionals < 2^53` and `fractionals * 2^exponent < 1`.
- `exponent`: `int`, `-128 <= exponent <= 0`. For `exponent == 0` the fractionals are 0.
- `fractional_count`: `int`, `0 <= fractional_count <= 100`.
- `buffer`: `Vector<char>` large enough for `*length + fractional_count` characters (the existing digits are ASCII `'0'..'9'`). `length`, `decimal_point`: non-null pointers to the current number of digits and the current decimal point position.

## 4. Output specification

`buffer[0 .. *length)`, `*length`, and `*decimal_point` as described. No return value.

## 5. Edge cases and constraints

Each row gives the arguments, the digits already in the buffer with the initial decimal point, and the result.

| fractionals | exponent | fractional_count | buffer before (`*decimal_point`) | buffer after (`*decimal_point`) |
|---|---|---|---|---|
| 1 | -1 | 0 | empty (0) | `1` (1) |
| 1 | -1 | 5 | empty (0) | `5` (0) |
| 1 | -1 | 0 | `12` (2) | `13` (2) |
| 3 | -3 | 2 | empty (0) | `38` (0) |
| 3 | -3 | 3 | empty (0) | `375` (0) |
| 1 | -4 | 2 | empty (0) | `06` (0) |
| 1 | -4 | 6 | empty (0) | `0625` (0) |
| 1 | -10 | 3 | empty (0) | `001` (0) |
| 1 | -10 | 3 | `7` (1) | `7001` (1) |
| 7 | -3 | 1 | `199` (3) | `1999` (3) |
| 15 | -4 | 1 | `9` (1) | `99` (1) |
| 15 | -4 | 0 | `9` (1) | `1` (2) |
| 1 | -3 | 0 | empty (0) | empty (0) |
| 7 | -3 | 0 | empty (0) | `1` (1) |
| 0 | 0 | 5 | `4` (1) | `4` (1) |
| 1 | -2 | 1 | empty (0) | `3` (0) |
| 1 | -100 | 4 | empty (0) | `0000` (0) |
| 1 | -100 | 40 | empty (0) | `0000000000000000000000000000007888609052` (0) |

The loop is bounded by `fractional_count`; the largest calls produce a few dozen digits, and all arithmetic must be exact (no floating point).
