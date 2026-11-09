You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `fmt_helper::pad2(n, dest)`

## 1. Component overview

A formatting helper of spdlog used to write the two-digit fields of a timestamp (month, day, hour, minute, second). It appends the decimal representation of a small integer to a character buffer, zero-padded to at least two digits.

## 2. Functional requirements

The function appends characters to the end of `dest` (it never removes or changes what is already in `dest`):

1. `n` in 0..9: a `0` followed by the digit (`"00"`, `"03"`, `"09"`).
2. `n` in 10..99: the two decimal digits (`"10"`, `"23"`, `"99"`).
3. `n` greater than 99: the plain decimal representation, with no padding and no truncation (`"100"`, `"123"`, `"1234"`, `"2147483647"`).
4. `n` negative: the plain decimal representation with a leading minus sign and no extra zeros (`-5` gives `"-5"`, `-100` gives `"-100"`, `-2147483648` gives `"-2147483648"`).

## 3. Input specification

- `n`: any `int`.
- `dest`: a `fmt::basic_memory_buffer<char, Buffer_Size>` (any `Buffer_Size`), possibly already containing text.

## 4. Output specification

No return value. Exactly the characters described above are appended to `dest`.

## 5. Edge cases and constraints

| `n` | appended text |
|---|---|
| 0 | `00` |
| 3 | `03` |
| 9 | `09` |
| 10 | `10` |
| 23 | `23` |
| 99 | `99` |
| 100 | `100` |
| 1234 | `1234` |
| -5 | `-5` |
| -42 | `-42` |

The function is called several times per logged line, so it must be fast and must not allocate beyond what the buffer itself needs.

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
spdlog::details::fmt_helper::pad3( T n , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::pad6( T n , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::pad9( T n , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::pad_uint( T n , unsigned int width , fmt :: basic_memory_buffer<char,Buffer_Size> & dest)
spdlog::details::fmt_helper::time_fraction( const log_clock :: time_point & tp)
spdlog::details::fmt_helper::to_string_view( const fmt :: basic_memory_buffer<char,Buffer_Size> & buf)
```

## Declaration line preceding the stub

The following line stands directly above the stub in the source file and is NOT part of your answer (do not repeat it):

```
template<size_t Buffer_Size>
```

The stub is inside `namespace spdlog { namespace details { namespace fmt_helper { ... } } }`. `fmt::basic_memory_buffer<char, N>` is the bundled fmt library's growable character buffer (`push_back(char)`, `append(const char* begin, const char* end)`, `data()`, `size()`); `fmt::format_to(buffer, "{:02}", n)` and `append_int` are available.

=== STUB ===
```cpp
inline void pad2(int n, fmt::basic_memory_buffer<char, Buffer_Size> &dest)
{
    // TODO: implement according to the specification
}
```
