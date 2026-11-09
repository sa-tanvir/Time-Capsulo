You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
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

=== STUB ===
```cpp
int Bignum::PlusCompare(const Bignum& a, const Bignum& b, const Bignum& c) {
    // TODO: implement according to the specification
}
```
