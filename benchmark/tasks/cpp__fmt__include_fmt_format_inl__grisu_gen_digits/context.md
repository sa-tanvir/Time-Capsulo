# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/format-inl.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`
- **Enclosing scope:** a function template at namespace level.

## Declaration line preceding the stub

The following line stands directly above the stub in the source file and is NOT part of your answer (do not repeat it):

```
template <typename Handler>
```

`FMT_ALWAYS_INLINE` is a macro (a compiler `always_inline` attribute); keep it as in the stub. `FMT_ASSERT(condition, message)` is an assert-like macro; `FMT_ASSERT(false, "...")` may be used for unreachable cases.

## Types and helpers visible to the function

```
struct fp {                         // a number f * 2^e with a 64-bit significand
  uint64_t f;
  int e;
  fp(uint64_t f_val, int e_val);    // constructor (also a default constructor exists)
};

namespace digits {
enum result {
  more,   // Generate more digits.
  done,   // Done generating digits.
  error   // Digit generation cancelled due to an error.
};
}

// Number of decimal digits of n (n >= 1); 1 for 0..9, 2 for 10..99, ...
inline int count_digits(uint32_t n);

struct data {   // (shown partially)
  static const uint64_t powers_of_10_64[];   // powers_of_10_64[i] == 10^i for i = 0 .. 19
};
```

## The Handler concept

`Handler` is a user supplied type. It receives the digits one at a time and decides when to stop:

```
digits::result on_start(uint64_t divisor, uint64_t remainder, uint64_t error, int& exp);
digits::result on_digit(char digit, uint64_t divisor, uint64_t remainder, uint64_t error, int exp, bool integral);
```

The two handlers in the library are `fixed_handler` (stops after a requested number of digits and rounds the last one, see its `on_digit`) and `grisu_shortest_handler` (stops when the digits uniquely identify the number). Their behaviour is not part of this task; call the handler's functions exactly as specified and use the results.

## Callers (for orientation only)

```
// format_float(), fixed precision:   normalized = normalize(fp(value)) * cached power of ten;
//     fixed_handler handler{buf.data(), 0, precision, -cached_exp10, fixed};
//     grisu_gen_digits(normalized, 1, exp, handler);
// format_float(), shortest:          grisu_gen_digits(fp(boundaries.upper, fp_value.e), boundaries.upper - boundaries.lower, exp, handler)
```
