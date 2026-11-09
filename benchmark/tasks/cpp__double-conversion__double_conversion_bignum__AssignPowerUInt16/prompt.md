You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `double-conversion/bignum.cc` (namespace `double_conversion`)
- **Target:** the definition of the public member function `Bignum::AssignPowerUInt16`. Keep the signature exactly as in the stub. As a member it may use the private members below. Do not add includes or other functions.

## Includes available in this file

```
#include "bignum.h"
#include "utils.h"
```

## Instance state (class `Bignum`)

```
static const int kMaxSignificantBits = 3584;       // = 128 * 28
typedef uint32_t Chunk;
typedef uint64_t DoubleChunk;
static const int kBigitSize = 28;                  // every stored bigit (big digit) uses only its low 28 bits
static const Chunk kBigitMask = (1 << kBigitSize) - 1;
static const int kBigitCapacity = kMaxSignificantBits / kBigitSize;   // 128

Chunk bigits_buffer_[kBigitCapacity];              // storage
Vector<Chunk> bigits_;                             // vector over bigits_buffer_ (bounds-checked in debug builds)
int used_digits_;                                  // number of stored bigits; bigits_[0] is the least significant one
int exponent_;                                     // number of implicit zero bigits below bigits_[0]
// value = sum over i in [0, used_digits_) of bigits_[i] * 2^(kBigitSize * (i + exponent_))
```

A valid ("clamped") bignum has a non-zero highest stored bigit, and the value zero is `used_digits_ == 0 && exponent_ == 0`. Public operations never grow beyond `kBigitCapacity` stored bigits and there are no overflow checks (the caller guarantees the size).

## Members you can call (all declared in `bignum.h`; their definitions are in the same file)

```
void EnsureCapacity(int size);       // private; calls UNREACHABLE() when size > kBigitCapacity (no growth: storage is fixed)
void Zero();                         // private; sets the value to 0 (used_digits_ = 0, exponent_ = 0, stored bigits cleared)
void Clamp();                        // private; drops zero bigits at the top; a zero value gets exponent_ = 0
void AssignUInt16(uint16_t value);   // sets the value (previous value discarded)
void AssignUInt64(uint64_t value);   // sets the value (previous value discarded)
void AssignBignum(const Bignum& other);
void AddUInt64(uint64_t operand);
void AddBignum(const Bignum& other);
void Square();                       // this = this * this
void ShiftLeft(int shift_amount);    // this = this * 2^shift_amount (shift_amount >= 0; whole bigits go to exponent_)
void MultiplyByUInt32(uint32_t factor);
void MultiplyByUInt64(uint64_t factor);
void MultiplyByPowerOfTen(int exponent);
void Times10();                      // MultiplyByUInt32(10)
bool ToHexString(char* buffer, int buffer_size) const;
static int Compare(const Bignum& a, const Bignum& b);
```

Callers (for orientation): `Bignum::AssignPowerUInt16(10, k)`-style calls appear in the digit generators and in the tests `test-bignum/AssignPowerUInt16`, which compare `ToHexString()` of the results with exact strings for bases 10, 2, 5, 16, 256 and so on.

=== STUB ===
```cpp
void Bignum::AssignPowerUInt16(uint16_t base, int power_exponent) {
    // TODO: implement according to the specification
}
```
