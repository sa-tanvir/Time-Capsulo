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
