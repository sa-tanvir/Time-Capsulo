You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `format_float(value, precision, specs, buf)`

## 1. Component overview

Converts a non-negative floating-point number to decimal "digits and exponent" form for fmt's floating-point formatting. The digits are stored in `buf` (ASCII, not NUL-terminated, `buf.size()` = number of digits) and the function returns a decimal exponent `e`, so that the number is approximately `digits * 10^e` (the digit string read as an integer). A later stage places the decimal point, signs, padding and exponent text, so the digit conventions below must be followed exactly.

## 2. Functional requirements

`value >= 0` (a negative value is never passed), finite. `specs.format` is `general`, `exp` or `fixed`. `buf` is empty on entry with capacity of at least a few hundred characters. `precision` has the meaning given by the caller: for `fixed` it is the number of digits after the decimal point (>= 0); for `general` and `exp` it is the number of significant digits (>= 1); `-1` means no precision (shortest representation, see rule 5).

1. **Zero.** If `value == 0`: if `precision <= 0` or the format is not `fixed`, the buffer becomes the single digit `0` and the function returns 0; otherwise (`fixed`, `precision > 0`) the buffer becomes `precision` characters `'0'` and the function returns `-precision`.
2. **Without the fast generator.** If `specs.use_grisu` is false, the result is exactly what `snprintf_float(value, precision, specs, buf)` produces (digits in `buf` and its return value).
3. **High precision.** If `precision > 17` the result is also exactly that of `snprintf_float(value, precision, specs, buf)`.
4. **Fixed number of digits (`0 <= precision <= 17`, `use_grisu` set).**
   - `fixed`: let `q` be `value * 10^precision` rounded to the nearest integer, ties to even (exact decimal value of the binary number, correct rounding). The buffer holds the decimal digits of `q` without leading zeros and the function returns `-precision`. If `q` is zero the buffer holds the single digit `0` or is empty (callers print zero in both cases) and the returned exponent is `-precision`. (Exactness is only guaranteed while the number of integer digits plus `precision` does not exceed 17.)
   - `general` / `exp` (`precision >= 1`): the buffer holds the `precision` most significant decimal digits of `value`, correctly rounded (nearest, ties to even on the exact binary value), **with trailing zeros removed**; every removed zero increases the returned exponent by one. Example: `1500.0` with precision 6 gives digits `15` and returns 2; `100.0` with precision 3 gives `1` and 2; `0.001` with precision 3 gives `1` and -3; `123.456` with precision 3 gives `123` and 0; `99.99` with precision 3 gives `1` and 2 (rounds up to 100).
5. **Shortest representation (`precision == -1`, `use_grisu` set).** The buffer holds the shortest decimal digit string that, read back as a number of the same type, gives exactly `value` (if several of the shortest length exist, the one closest to `value`), without trailing zeros; the function returns the exponent such that `digits * 10^e` is that decimal. If `specs.binary32` is set the value is a float promoted to double and "read back" is as a float. Examples: `0.1` gives `1`, -1; `100.0` gives `1`, 2; `123.456` gives `123456`, -3; `5e-324` gives `5`, -324; `1e22` gives `1`, 22; `0.99960000000000004` gives `9996`, -4.

When rule 2 or 3 applies the digit conventions of `snprintf_float` (including its handling of `fixed`, where leading zeros of the integer part are kept) are used, so those results differ in form from rule 4; both forms are accepted by the later stage.

## 3. Input specification

- `T` is `double` or `long double`; `long double` is always called with `use_grisu` false.
- `value` finite, `>= 0`. `precision` as above; `fixed` is never called with `-1`, `general`/`exp` are never called with `0`.
- `specs.use_grisu`, `specs.binary32` as described; the `trailing_zeros`, `upper`, `sign`, `locale`, `percent` members do not affect the digits (except through `snprintf_float` where it documents them).

## 4. Output specification

Returns the decimal exponent `e` and leaves the digits in `buf` as described. No exceptions. Behaviour for precondition violations is unspecified.

## 5. Edge cases and constraints

- Denormals (`5e-324`) and the largest doubles (`1.7976931348623157e308`) are valid inputs: shortest gives `17976931348623157` and 292.
- Rounding must be correct to the last digit: `fixed` with precision 2: `1.005` (really 1.00499999999999989...) gives `100`, -2; `0.5` with precision 0 gives `0` (tie to even); `1.5` gives `2`; `2.5` gives `2`.
- `fixed`, `precision` 2, `0.001` gives a zero result (`0` or empty) with exponent `-2`.
- Trailing zeros are only stripped for `general`/`exp` (rule 4) and in rule 5; `fixed` keeps all `integer digits + precision` digits (`100.0` with precision 2 gives `10000`, -2).

=== CONTEXT ===
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

=== STUB ===
```cpp
int format_float(T value, int precision, float_specs specs, buffer<char>& buf) {
    // TODO: implement according to the specification
}
```
