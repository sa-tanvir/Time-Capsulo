You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `snprintf_float(value, precision, specs, buf)`

## 1. Component overview

A fallback formatter of the fmt library for floating-point numbers. It uses the C library's `printf` family to produce the decimal digits of `value` and returns them to the caller in a normalised "digits and decimal exponent" form (digits in `buf`, exponent as the return value), or, for the hexadecimal format, the complete printed text. It is used for `long double`, for requests that the fast algorithm cannot handle (high precision, hex), and as a general fallback.

## 2. Functional requirements

`value` is finite and non-negative. `specs.format` is `general`, `exp`, `fixed` or `hex`. The text of the number is produced as `printf` would (C locale, correctly rounded) with a conversion chosen from `specs`; results are appended to `buf` (after the characters it already contains) and `buf` must grow as needed so that the whole result fits. The buffer is not NUL-terminated at the end and `buf.size()` must be exactly the number of characters of the result (existing characters included).

**Conversion.**
- `hex`: `%a`, or `%A` when `specs.upper` is set. `fixed`: `%f`. `general` and `exp`: `%e`. (`specs.upper` has no effect on `e` and `f`.)
- For `long double` values the length modifier `L` is used.
- When `specs.trailing_zeros` is set the `#` flag is used.
- For `fixed` and `hex` the `precision` argument is given to `printf` as its precision when it is non-negative; a negative one means "no precision" (printf's default, 6 fractional digits for `f`).
- For `general` and `exp` the argument counts significant digits, so `printf` receives one less: `precision` 1 gives `%.0e`, 3 gives `%.2e`, 17 gives `%.16e`. A negative `precision` means 6 significant digits (`%.5e`). `precision` 0 gives `printf` the precision -1, which means no precision at all (`%e`: 6 digits after the first).

**Result by format.** Let `T` be the text printed by `printf`.
1. `hex`: the characters of `T` are appended unchanged (e.g. `0x1.8p+0`, `0X1.8P+0`, `0x1p-1`, with `#`: `0x1.p-1`); the function returns 0.
2. `fixed`:
   - if the printf precision is exactly 0: `T` is appended unchanged (with the `#` flag it therefore ends in `.`); the function returns 0.
   - otherwise the decimal point is removed from `T` and the rest (integer digits followed by fractional digits, leading zeros of the integer part such as in `0.0012` kept: `00012`) is appended; the function returns minus the number of fractional digits (`-6` for the default). Example: `2.5` with precision 3 appends `2500` and returns `-3`; `0.001` with precision 2 appends `000` and returns `-2`; `123.456` with no precision appends `123456000` and returns `-6`.
3. `general` / `exp` (T has the form `d[.ddd]e(+|-)XX`): let `E` be the decimal exponent printed in `T`. The first digit and the fractional digits are appended with the decimal point removed and **trailing zeros of the fractional part removed** (the first digit is always kept, even if it is `0`); with `F` the number of fractional digits kept, the function returns `E - F`, so that the appended digits times 10 to the power of the return value equal the printed number. Examples: `1500.0` with precision -1 appends `15`, returns 2; `100.0` with precision 3 appends `1`, returns 2; `0.5` with precision 10 appends `5`, returns -1; `2.5` with precision 0 (treated as no precision) appends `25` and returns -1; `123456.0` with precision 2 (`1.2e+05`) appends `12`, returns 4; `0.0` appends `0` and returns 0.

## 3. Input specification

- `T`: `double` or `long double`. `value >= 0`, finite (denormals, very large values such as 1e308 are possible; large `fixed` results have hundreds of digits).
- `precision`: `-1` (none) or any non-negative value (up to a few dozen in practice).
- `buf`: a buffer with `capacity() > size()`. For the `fixed` and `general`/`exp` formats it is empty on entry; for `hex` it may already contain a sign character (appended text goes after it).

## 4. Output specification

Returns the decimal exponent described above (0 for hex and for fixed with printf precision 0). `buf` ends with its original contents followed by the digit text described above (not NUL-terminated, `size()` exact). No exceptions.

## 5. Edge cases and constraints

- Very small and very large values: output length is only limited by `printf` (a `fixed` print of 1e300 has over 300 digits), so the buffer must be able to grow.
- `0.0` gives digits `0`, return 0 for `general`/`exp`; for `fixed` with precision 2 it gives `000` and `-2`.
- `fixed` with precision 0 and no `#`: `392.5` prints `392` (round to even) and returns 0; with `#` the buffer holds `392.`.
- The digits of the rounded result are exactly those `printf` prints; do not apply any additional rounding.

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/format-inl.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`
- **Enclosing scope:** a function template at namespace level (declared earlier in `format.h` as `template <typename T> int snprintf_float(T value, int precision, float_specs specs, buffer<char>& buf);`).

## Declaration line preceding the stub

The following line stands directly above the stub in the source file and is NOT part of your answer (do not repeat it):

```
template <typename T>
```

`T` is `double` or `long double` (never `float`; the original has `static_assert(!std::is_same<T, float>(), "")`).

## Includes available

```
#include "format.h"   // and, through it, <cstring>, <cstdio>, <cassert>, <algorithm>, <cstdint>, <limits>, <memory>
```

`FMT_ASSERT(condition, message)` is an assert-like macro. The macro `FMT_SNPRINTF` expands to a function with the semantics of the C `snprintf` (it may be used as `FMT_SNPRINTF(char* dest, size_t capacity, const char* format, ...)`, returning the number of characters the full output needs, or a negative value on error). You may use `<cstdio>`/`<cstring>` functions directly. The process runs in the default "C" locale.

## Types used

```
enum class float_format : unsigned char {
  general,  // General: exponent notation or fixed point based on magnitude.
  exp,      // Exponent notation with the default precision of 6, e.g. 1.2e-3.
  fixed,    // Fixed point with the default precision of 6, e.g. 0.0012.
  hex
};

struct float_specs {
  int precision;
  float_format format : 8;
  sign_t sign : 8;
  bool upper : 1;           // upper case hex digits/prefix/exponent ('A' conversion)
  bool locale : 1;
  bool percent : 1;
  bool binary32 : 1;
  bool use_grisu : 1;
  bool trailing_zeros : 1;  // keep the decimal point / trailing zeros ('#' flag)
};

// Abstract growable character buffer (also the base class of memory_buffer):
template <typename T> class buffer {
 public:
  T* data();                       // pointer to the first element
  std::size_t size() const;        // number of elements
  std::size_t capacity() const;    // elements that fit without growing
  void resize(std::size_t new_size);   // changes size; growing beyond capacity grows the storage (contents are kept)
  void reserve(std::size_t new_capacity);   // makes capacity >= new_capacity, keeping the contents
  void push_back(const T& value);
};
```

`to_unsigned(int)` (conversion of a non-negative int to the unsigned type of the same width) is available.

## Callers (for orientation only)

```
// format_float(): return snprintf_float(value, precision, specs, buf);   // when the fast digit generator can't be used
// basic_writer::write(): for hex: if (sign) buffer.push_back('-' or '+' or ' '); snprintf_float(promote_float(value), specs.precision, fspecs, buffer);
```

=== STUB ===
```cpp
int snprintf_float(T value, int precision, float_specs specs,
                   buffer<char>& buf) {
    // TODO: implement according to the specification
}
```
