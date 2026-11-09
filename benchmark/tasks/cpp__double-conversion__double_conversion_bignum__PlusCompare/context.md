# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `double-conversion/bignum.cc` (namespace `double_conversion`)
- **Target:** the definition of the public static member function `Bignum::PlusCompare`. Keep the signature exactly as in the stub. You may use the private members below (the function is a member).

## Includes available in this file

```
#include "bignum.h"
#include "utils.h"
```

## Instance state (class `Bignum`, private members relevant to the function)

```
typedef uint32_t Chunk;
typedef uint64_t DoubleChunk;
static const int kChunkSize = 32;
static const int kBigitSize = 28;                  // every stored bigit (big digit) uses only its low 28 bits
static const Chunk kBigitMask = (1 << kBigitSize) - 1;

Chunk bigits_buffer_[kBigitCapacity];              // storage (128 chunks)
Vector<Chunk> bigits_;                             // vector over bigits_buffer_ (bounds-checked in debug builds)
int used_digits_;                                  // number of stored bigits; bigits_[0] is the least significant one
int exponent_;                                     // number of implicit 0-bigits below bigits_[0]
// value = sum over i in [0, used_digits_) of bigits_[i] * 2^(kBigitSize * (i + exponent_))

int BigitLength() const { return used_digits_ + exponent_; }   // index of the top bigit + 1, including the implicit zero bigits
Chunk BigitAt(int index) const;     // bigit number 'index' of the full value (0 <= index): 0 if index < exponent_ or index >= BigitLength(),
                                    // otherwise bigits_[index - exponent_]
bool IsClamped() const;             // true if used_digits_ == 0 or the highest stored bigit is non-zero
```

Normalised ("clamped") means `IsClamped()` and, for the value zero, `used_digits_ == 0 && exponent_ == 0`. All public operations leave bignums normalised, and all arguments of `PlusCompare` are normalised. The bigits stored below the lowest non-zero one may be zero; the implicit zero bigits (`exponent_`) only record trailing zero bigits.

Helpers available (in `utils.h`): `template <typename T> static T Max(T a, T b)`, `template <typename T> static T Min(T a, T b)`, and the `ASSERT` macro.

## Public interface of the class (for orientation)

```
static int Compare(const Bignum& a, const Bignum& b);                   // three-way comparison, -1 / 0 / +1
static bool PlusEqual(const Bignum& a, const Bignum& b, const Bignum& c)     { return PlusCompare(a, b, c) == 0; }
static bool PlusLessEqual(const Bignum& a, const Bignum& b, const Bignum& c) { return PlusCompare(a, b, c) <= 0; }
static bool PlusLess(const Bignum& a, const Bignum& b, const Bignum& c)      { return PlusCompare(a, b, c) < 0; }
```
