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
