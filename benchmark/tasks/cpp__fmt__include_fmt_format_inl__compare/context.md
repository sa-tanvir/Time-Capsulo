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
