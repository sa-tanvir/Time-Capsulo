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
