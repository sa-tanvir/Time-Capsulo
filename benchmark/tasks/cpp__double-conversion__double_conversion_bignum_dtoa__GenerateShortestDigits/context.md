# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `double-conversion/bignum-dtoa.cc` (namespace `double_conversion`)
- **Target:** a file-local (`static`) function. Keep the signature exactly as in the stub. It is called from `BignumDtoa` in the same file for the modes SHORTEST and SHORTEST_SINGLE.

## Includes available in this file

```
#include <cmath>
#include "bignum-dtoa.h"
#include "bignum.h"
#include "ieee.h"      // Double, Single, DiyFp
```
(`utils.h` is included through `bignum.h`: `Vector<T>`, `ASSERT`, `uint16_t`, ...)

## Types you work with

```
template <typename T> class Vector {            // simplified view over caller-owned memory
 public:
  Vector(T* data, int len);
  int length() const;
  T* start() const;
  T& operator[](int index) const;               // buffer[i] is a reference to the i-th element
};

class Bignum {                                  // non-negative arbitrary-precision integer, fixed capacity
 public:
  void AssignUInt16(uint16_t value);
  void AssignUInt64(uint64_t value);
  void AddBignum(const Bignum& other);
  void SubtractBignum(const Bignum& other);     // precondition: this >= other
  void ShiftLeft(int shift_amount);
  void MultiplyByUInt32(uint32_t factor);
  void Times10();                               // this *= 10
  // Pseudocode:  int result = this / other;  this = this % other;   (result is returned; it must fit in 16 bits)
  uint16_t DivideModuloIntBignum(const Bignum& other);
  static int  Compare(const Bignum& a, const Bignum& b);          // -1 / 0 / +1
  static bool Equal(const Bignum& a, const Bignum& b);            // a == b
  static bool LessEqual(const Bignum& a, const Bignum& b);        // a <= b
  static bool Less(const Bignum& a, const Bignum& b);             // a <  b
  static int  PlusCompare(const Bignum& a, const Bignum& b, const Bignum& c);   // Compare(a + b, c)
  static bool PlusEqual(const Bignum& a, const Bignum& b, const Bignum& c);     // a + b == c
  static bool PlusLessEqual(const Bignum& a, const Bignum& b, const Bignum& c); // a + b <= c
  static bool PlusLess(const Bignum& a, const Bignum& b, const Bignum& c);      // a + b <  c
};
```

## Caller (for orientation only)

```
// in BignumDtoa(double v, BignumDtoaMode mode, ...), after the scaled start values have been computed:
//   v = (numerator / denominator) * 10^(decimal_point-1), and 1 <= (numerator + delta_plus) / denominator < 10
case BIGNUM_DTOA_SHORTEST: case BIGNUM_DTOA_SHORTEST_SINGLE:
  GenerateShortestDigits(&numerator, &denominator, &delta_minus, &delta_plus, is_even, buffer, length);
  break;
// afterwards:  buffer[*length] = '\0';
```

Other functions in the same file (not needed): `NormalizedExponent`, `EstimatePower`, `InitialScaledStartValues`, `FixupMultiply10`, `BignumToFixed`, `GenerateCountedDigits`, `BignumDtoa`.
