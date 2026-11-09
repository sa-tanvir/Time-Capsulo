You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `fmt_helper::pad_uint(n, width, dest)`

## 1. Component overview

A formatting helper of spdlog used to write the fractional-second fields of a timestamp (milliseconds, microseconds, nanoseconds) and the message counter. It appends an unsigned integer to a character buffer in decimal, left-padded with `0` characters to a minimum number of digits.

## 2. Functional requirements

Appends to the end of `dest` (existing content is kept) the decimal representation of `n`, preceded by as many `0` characters as are needed for the whole appended text to have at least `width` characters:

1. Let `d` be the number of decimal digits of `n` (`d == 1` for `n == 0`).
2. If `width > d`, append `width - d` zero characters first.
3. Then append the digits of `n` (no sign, no separators, no leading zeros of its own).

The number is never truncated: if `n` has more digits than `width`, only its digits are appended. `width == 0` therefore means "no padding".

## 3. Input specification

- `n`: a value of the unsigned integer type `T` (`unsigned short`, `unsigned int`, `unsigned long`, `unsigned long long`; the full range of the type, e.g. up to 18446744073709551615 for 64 bits).
- `width`: `unsigned int`, from 0 to 20 inclusive (larger widths are outside the contract).
- `dest`: a `fmt::basic_memory_buffer<char, Buffer_Size>`, possibly already containing text.

## 4. Output specification

No return value; only `dest` grows by the text described above. No exceptions for valid input.

## 5. Edge cases and constraints

| `n` | `width` | appended |
|---|---|---|
| 0 | 3 | `000` |
| 3 | 3 | `003` |
| 123 | 3 | `123` |
| 1234 | 3 | `1234` |
| 12345 | 6 | `012345` |
| 123456789 | 9 | `123456789` |
| 1234567891 | 9 | `1234567891` |
| 7 | 0 | `7` |
| 7 | 1 | `7` |
| 0 | 1 | `0` |
| 42 | 12 | `000000000042` |
| 18446744073709551615 | 20 | `18446744073709551615` |
| 18446744073709551615 | 3 | `18446744073709551615` |

The helper is called for every logged line, so it must be fast and avoid temporary allocations.

=== CONTEXT ===
# Context for the function to implement

- **Language:** cpp
- **File:** `include/spdlog/details/fmt_helper.h`

## Imports / includes available in this file

```
#include <chrono>
#include <type_traits>
#include "spdlog/fmt/fmt.h"
```

## Other functions defined in the same file (signatures only; you may call them)

```
spdlog::details::fmt_helper::append_buf( const fmt :: basic_memory_buffer<char,Buffer_Size1> & buf , fmt :: basic_memory_buffer<char,Buffer_Size2> & dest)
spdlog::details::fmt_helper::append_int( T n , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::append_string_view( spdlog :: string_view_t view , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::count_digits( T n)
spdlog::details::fmt_helper::pad2( int n , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::pad3( T n , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::pad6( T n , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::pad9( T n , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::time_fraction( const log_clock :: time_point & tp)
spdlog::details::fmt_helper::to_string_view( const fmt :: basic_memory_buffer<char,Buffer_Size> & buf)
```

## Declaration line preceding the stub

The following line stands directly above the stub in the source file and is NOT part of your answer (do not repeat it):

```
template<typename T, size_t Buffer_Size>
```

The stub is inside `namespace spdlog { namespace details { namespace fmt_helper { ... } } }`. `T` is an unsigned integer type (the original code has a `static_assert` that `T` is unsigned; callers use `unsigned short`, `uint32_t`, `uint64_t` and `std::size_t`). `fmt::basic_memory_buffer<char, N>` is the bundled fmt library's growable character buffer (`push_back(char)`, `append(const char* begin, const char* end)`, `data()`, `size()`). The helpers `count_digits(n)` (number of decimal digits, 1 for 0) and `append_int(n, dest)` listed above can be used.

=== STUB ===
```cpp
inline void pad_uint(T n, unsigned int width, fmt::basic_memory_buffer<char, Buffer_Size> &dest)
{
    // TODO: implement according to the specification
}
```
