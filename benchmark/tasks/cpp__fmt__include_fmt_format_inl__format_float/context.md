# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/format-inl.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`
- **Enclosing scope:** a function template at namespace level (declared earlier in `format.h` as `template <typename T> int format_float(T value, int precision, float_specs specs, buffer<char>& buf);`).

## Declaration line preceding the stub

The following line stands directly above the stub in the source file and is NOT part of your answer (do not repeat it):

```
template <typename T>
```

`T` is `double` or `long double` (never `float`; callers promote floats to double and set `specs.binary32`).

## Types used

```
enum class float_format : unsigned char { general, exp, fixed, hex };

struct float_specs {
  int precision;
  float_format format : 8;
  sign_t sign : 8;
  bool upper : 1, locale : 1, percent : 1;
  bool binary32 : 1;        // value is exactly a float: "shortest" means the shortest digits that identify it as a float
  bool use_grisu : 1;       // the fast digit generator may be used (true for float and double on IEEE-754 platforms, false for long double)
  bool trailing_zeros : 1;
};

template <typename T> class buffer {   // growable character buffer (memory_buffer derives from it; its capacity is at least 500 here)
 public:
  T* data(); std::size_t size() const; std::size_t capacity() const;
  void resize(std::size_t new_size);  void reserve(std::size_t new_capacity);  void push_back(const T& value);
  T& operator[](std::size_t index);
};
```

`FMT_ASSERT(condition, message)` is an assert-like macro; `to_unsigned(int)` converts a non-negative int to unsigned.

## Functions and types available before this point in the file (same namespace; you may use them)

```
// Formats value with snprintf (see its own specification): digits in buf, returns the decimal exponent.
template <typename T> int snprintf_float(T value, int precision, float_specs specs, buffer<char>& buf);

struct fp {                        // a floating-point number f * 2^e with a 64-bit significand
  uint64_t f; int e;
  static const int significand_size = 64;
  fp(uint64_t f_val, int e_val);   fp();   template <typename Double> explicit fp(Double d);   // converts a double
  // (further members of fp, such as the functions that compute rounding boundaries, are internal to the original
  // implementation and are not described here)
};
fp normalize(fp value);            // shifts f left until its most significant bit is set
inline uint64_t multiply(uint64_t lhs, uint64_t rhs);   // upper 64 bits of the rounded 128-bit product
inline fp operator*(fp x, fp y);
fp get_cached_power(int min_exponent, int& pow10_exponent);   // power of ten with binary exponent >= min_exponent; its decimal exponent goes to pow10_exponent

// grisu_gen_digits, fixed_handler, grisu_shortest_handler and fallback_format are internal digit generators of the original
// implementation; their interfaces and conventions are NOT documented here, so do not rely on them.
```

(You do not have to use any of these; the specification below is purely about the result. The undocumented internals listed as such must not be relied upon: compute the result from the numeric rules below, e.g. with your own arithmetic or by calling `snprintf_float`.)

## Callers (for orientation only)

```
// basic_writer::write(double):  int exp = format_float(promote_float(value), precision, fspecs, buffer);
//   then float_writer<char>(buffer.data(), buffer.size(), exp, fspecs, point) prints the digits.
```
