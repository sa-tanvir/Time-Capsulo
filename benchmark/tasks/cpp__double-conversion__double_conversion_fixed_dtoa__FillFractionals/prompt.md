You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `double-conversion/fixed-dtoa.cc` (namespace `double_conversion`)
- **Target:** a file-local (`static`) function. Keep the signature exactly as in the stub.

## Includes available in this file

```
#include <cmath>
#include "fixed-dtoa.h"
#include "ieee.h"
```
(`utils.h` comes with them: `Vector<T>`, `ASSERT`, `uint64_t`, ...)

## Types and helpers available (defined earlier in the same file)

```
template <typename T> class Vector {            // simplified view over caller-owned memory
 public:
  Vector(T* data, int len);
  int length() const;
  T* start() const;
  T& operator[](int index) const;               // buffer[i] is a reference to the i-th element
};

// A 128-bit unsigned integer (high_bits_, low_bits_).
class UInt128 {
 public:
  UInt128();                                    // zero
  UInt128(uint64_t high, uint64_t low);
  void Multiply(uint32_t multiplicand);         // *this *= multiplicand   (the result must still fit in 128 bits)
  void Shift(int shift_amount);                 // -64 <= shift_amount <= 64; negative = shift left, positive = shift right
  int DivModPowerOf2(int power);                // returns *this / 2^power and sets *this = *this % 2^power; the quotient must fit an int
  bool IsZero() const;
  int BitAt(int position) const;                // 0 or 1; position in [0, 128)
};

// Rounds the digits in buffer[0 .. *length) up by one unit of the last digit (carry through '9's; a carry out of the
// first digit makes it '1' and increments *decimal_point). If *length == 0 it writes "1", sets *length = 1 and
// *decimal_point = 1.
static void RoundUp(Vector<char> buffer, int* length, int* decimal_point);
```
Other helpers in the file (not needed): `FillDigits32`, `FillDigits32FixedLength`, `FillDigits64`, `FillDigits64FixedLength`, `TrimZeros`, `FastFixedDtoa`.

## Caller (for orientation only)

```
// in FastFixedDtoa(), v = significand * 2^exponent with -53 < exponent < 0:
uint64_t integrals = significand >> -exponent;
uint64_t fractionals = significand - (integrals << -exponent);
... FillDigits32/64(integrals, buffer, length) ...
*decimal_point = *length;
FillFractionals(fractionals, exponent, fractional_count, buffer, length, decimal_point);
// and, for tiny numbers (-128 <= exponent <= -53):  *decimal_point = 0;  FillFractionals(significand, exponent, ...);
// afterwards TrimZeros(buffer, length, decimal_point) removes leading and trailing zeros
```

=== STUB ===
```cpp
static void FillFractionals(uint64_t fractionals, int exponent,
                            int fractional_count, Vector<char> buffer,
                            int* length, int* decimal_point) {
    // TODO: implement according to the specification
}
```
