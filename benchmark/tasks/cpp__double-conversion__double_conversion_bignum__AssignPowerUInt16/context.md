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
