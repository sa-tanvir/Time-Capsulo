# Context for the function to implement

- **Language:** cpp
- **File:** `include/spdlog/details/file_helper.h`

## Imports / includes available in this file

```
#include "spdlog/details/log_msg.h"
#include "spdlog/details/os.h"
#include <cerrno>
#include <chrono>
#include <cstdio>
#include <string>
#include <thread>
#include <tuple>
```

## Other functions defined in the same file (signatures only; you may call them)

```
spdlog::details::file_helper::close()
spdlog::details::file_helper::file_exists( const filename_t & fname)
spdlog::details::file_helper::filename() const
spdlog::details::file_helper::flush()
spdlog::details::file_helper::open( const filename_t & fname , bool truncate = false)
spdlog::details::file_helper::reopen( bool truncate)
spdlog::details::file_helper::size() const
spdlog::details::file_helper::write( const fmt :: memory_buffer & buf)
spdlog::details::file_helper::~file_helper()
```

## Where the stub lives

The stub is the body of the `static` member function `split_by_extension` of `class spdlog::details::file_helper` (header-only; the class is otherwise irrelevant here). Keep the `static` keyword exactly as in the stub.

```cpp
namespace spdlog {
using filename_t = std::string;              // narrow file names in this build
namespace details { namespace os {
SPDLOG_CONSTEXPR static const char folder_sep = '/';   // the only folder separator in this (Linux) build
}}}
```
`<tuple>` is included; the result is a `std::tuple<filename_t, filename_t>` (use `std::make_tuple`).
