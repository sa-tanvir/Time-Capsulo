# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/format-inl.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`
- **Enclosing scope:** the member function is defined inside `struct fixed_handler`, shown below. The stub is one of its member functions (the surrounding struct and the sibling member `on_start` are not part of your answer).

## Types and helpers visible to the function

```
#define FMT_ASSERT(condition, message)   // assert-like macro

enum round_direction { unknown, up, down };

// Given the divisor (normally a power of 10), the remainder = v % divisor for some number v and the error, returns
// whether v should be rounded up, down, or whether the rounding direction can't be determined due to error.
// Requires remainder < divisor and error < divisor - error.
inline round_direction get_round_direction(uint64_t divisor, uint64_t remainder, uint64_t error);

namespace digits {
enum result {
  more,   // Generate more digits.
  done,   // Done generating digits.
  error   // Digit generation cancelled due to an error.
};
}
```

## The enclosing struct (fixed-precision digit handler used by the Grisu digit generator)

```
struct fixed_handler {
  char* buf;        // output buffer; the digits generated so far are buf[0 .. size-1] (ASCII '0'..'9'); it has room for one more character than the digits
  int size;         // number of digits stored so far
  int precision;    // number of digits wanted (after on_start has adjusted it)
  int exp10;        // decimal exponent adjustment (not used by on_digit)
  bool fixed;       // fixed-point format flag (not used by on_digit)

  digits::result on_start(uint64_t divisor, uint64_t remainder, uint64_t error, int& exp);   // sibling, not to be implemented

  digits::result on_digit(char digit, uint64_t divisor, uint64_t remainder,
                          uint64_t error, int, bool integral);   // <-- the stub
};
```

## Caller (for orientation only)

```
// grisu_gen_digits(): after producing each next decimal digit it calls
//   result = handler.on_digit('0' + digit, power_of_10 << -one.e, remainder, error, exp, integral_part_flag);
//   if (result != digits::more) return result;
```
