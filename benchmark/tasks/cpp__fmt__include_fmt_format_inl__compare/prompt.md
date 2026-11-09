You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `compare(lhs, rhs)` for `bigint`

## 1. Component overview

`bigint` is fmt's small unsigned arbitrary-precision integer type, used by the exact (slow-path) floating-point printing algorithm. `compare` is the three-way comparison of two such numbers: it tells whether the first is smaller than, equal to or larger than the second.

## 2. Functional requirements

1. Return `-1` if the number `lhs` is smaller than `rhs`, `0` if they are equal and `1` if `lhs` is larger.
2. The numbers are compared by value, where the value of a bigint is `sum of bigits_[i] * 2^(32 * (i + exp_))` as described in the context. The two operands may have different numbers of stored bigits and different `exp_` values (for example `bigint(42) <<= 32` stores one bigit with `exp_` 1 while `bigint(42 * 0x100000001)` stores two bigits with `exp_` 0).
3. Both operands are normalised (see the context), so a number with more total bigits (`num_bigits()`) is always the larger one; for equal total bigit counts the numbers are compared from the most significant bigit downwards, and a number that has additional non-zero lower-order bigits that the other one lacks is the larger one when all the overlapping higher bigits are equal.
4. Neither operand is modified.

Examples (values): `42` and `42` give 0; `42` and `42 << 32` give -1 (and the reverse gives 1); `42` and `43` give -1; `43` and `42` give 1; `42 << 32` and `42 * (2^32 + 1)` give -1; `0` and `0` give 0; `0` and `1` give -1; `2^96` and `2^64` give 1; `10^100` and `10^100` give 0; `10^30 * 7` and `10^30 * 3` give 1.

## 3. Input specification

- `lhs`, `rhs`: bigints with at most 32 bigits stored, normalised as described; their `exp_` can be any non-negative value such that the total stays below about 2^1100.

## 4. Output specification

Returns an `int`: `-1`, `0` or `1` as described. Pure function, no exceptions, no allocation.

## 5. Edge cases and constraints

- Zero versus zero is equal; zero versus any positive number is smaller.
- Normalised numbers have a unique representation, so two equal numbers have the same `exp_` and identical stored bigits (and the reverse).
- Equal numbers require inspecting every stored bigit, so the function is linear in the number of stored bigits in the worst case.

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/format-inl.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`
- **Enclosing scope:** the stub is a *friend function defined inside* the class `bigint` (a non-negative arbitrary-precision integer used by the floating-point printing code). Being a friend it can access the private members of both arguments. The class itself and its other members are not part of your answer; keep the signature exactly as in the stub (including `friend`).

## Instance state (class `bigint`, private members read by the function)

```
class bigint {
 private:
  // A bigint is stored as an array of bigits (big digits, 32 bits each), with the bigit at index 0 being the least significant one.
  using bigit = uint32_t;
  basic_memory_buffer<bigit, 32> bigits_;   // the stored bigits: bigits_.size() elements, bigits_[i] for 0 <= i < size()
  int exp_;                                 // the stored bigits are shifted left by exp_ whole bigits (i.e. by 32 * exp_ bits)
                                            // value = sum over i of bigits_[i] * 2^(32 * (i + exp_))

  int num_bigits() const { return static_cast<int>(bigits_.size()) + exp_; }   // total number of bigits (index of the top bigit + 1)

 public:
  bigint();                                 // empty: no stored bigits, exp_ == 0 (value zero)
  explicit bigint(uint64_t n);              // stores n as one or two bigits, exp_ == 0 (the number 0 is stored as a single bigit 0)
  bigint& operator<<=(int shift);           // multiplies by 2^shift: shift / 32 whole bigits go into exp_, the rest is shifted inside the bigits
  template <typename Int> bigint& operator*=(Int value);   // multiplies in place
  void assign_pow10(int exp);               // sets the value to 10^exp
  ...                                       // other members

  friend int compare(const bigint& lhs, const bigint& rhs);       // <-- the stub
};
```

All bigints handled by the library are normalised: the highest stored bigit is non-zero and the lowest stored bigit is non-zero (the number zero is the single stored bigit 0 with `exp_` 0), because the low-order zero bigits are represented by `exp_` and never stored.

## Callers (for orientation only)

```
// bigint::subtract_aligned / divmod_assign:   FMT_ASSERT(compare(*this, other) >= 0, "");   while (compare(*this, divisor) >= 0) ...
// fallback_format():   bool low = compare(numerator, lower) - even < 0;
```

=== STUB ===
```cpp
friend int compare(const bigint& lhs, const bigint& rhs) {
    // TODO: implement according to the specification
}
```
