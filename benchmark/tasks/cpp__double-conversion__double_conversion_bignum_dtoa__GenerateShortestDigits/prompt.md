You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
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

=== STUB ===
```cpp
static void GenerateShortestDigits(Bignum* numerator, Bignum* denominator,
                                   Bignum* delta_minus, Bignum* delta_plus,
                                   bool is_even,
                                   Vector<char> buffer, int* length) {
    // TODO: implement according to the specification
}
```
