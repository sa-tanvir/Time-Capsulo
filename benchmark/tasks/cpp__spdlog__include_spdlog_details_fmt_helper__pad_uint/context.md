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
