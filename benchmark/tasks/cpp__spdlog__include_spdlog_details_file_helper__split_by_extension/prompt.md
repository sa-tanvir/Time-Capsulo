You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `file_helper::split_by_extension(fname)`

## 1. Component overview

A helper of spdlog's file sinks. It splits a file name or path into a *base* (the path without its extension) and an *extension* (including the leading dot), for example to insert a date or a rotation index before the extension. It is a pure string function.

## 2. Functional requirements

Let *last dot* be the position of the last `.` character in the whole string, and *last separator* the position of the last folder separator `/`.

The function returns a pair `(base, ext)` with `base + ext == fname` in every case.

1. If an extension is recognised, `ext` is the substring from the last dot to the end of the string (dot included) and `base` is everything before the last dot.
2. Otherwise `base` is the whole input and `ext` is the empty string.

The last dot does **not** start an extension (rule 2 applies) in any of these cases:
- there is no dot in the string;
- the last dot is the very first character of the string (a hidden file such as `.mylog`);
- the last dot is the very last character (`mylog.`, a trailing dot);
- there is a separator, and the last separator lies at or after the position immediately before the last dot. This covers a dot that belongs to a directory name (the last separator comes after the dot, as in `/aaa/bb.d/mylog`, `.././mylog.txt/xxx`) and a dot that directly follows a separator (a hidden file in a directory: `my_folder/.mylog`, `/abc/.hidden`).

Only the last dot is considered: `a.b.c` gives `("a.b", ".c")`. A dot that is not directly preceded by a separator and is not the first character is a valid extension start even when the base ends up looking odd (`..txt` gives `(".", ".txt")`, `a..b` gives `("a.", ".b")`).

## 3. Input specification

`fname`: any `std::string` (possibly empty, no embedded NUL), taken as a path using `/` as folder separator.

## 4. Output specification

A `std::tuple<std::string, std::string>` `(base, ext)` as described. No exceptions are thrown. The input is not modified.

## 5. Edge cases and constraints

| input | base | ext |
|---|---|---|
| `mylog.txt` | `mylog` | `.txt` |
| `.mylog.txt` | `.mylog` | `.txt` |
| `.mylog` | `.mylog` | (empty) |
| `/aaa/bb.d/mylog` | `/aaa/bb.d/mylog` | (empty) |
| `/aaa/bb.d/mylog.txt` | `/aaa/bb.d/mylog` | `.txt` |
| `aaa/bbb/ccc/mylog.` | `aaa/bbb/ccc/mylog.` | (empty) |
| `aaa/bbb/ccc/.mylog.txt` | `aaa/bbb/ccc/.mylog` | `.txt` |
| `/aaa/bbb/ccc/.mylog` | `/aaa/bbb/ccc/.mylog` | (empty) |
| `../mylog.txt` | `../mylog` | `.txt` |
| `.././mylog.txt/xxx` | `.././mylog.txt/xxx` | (empty) |
| `//mylog.txt` | `//mylog` | `.txt` |
| (empty string) | (empty) | (empty) |
| `.` | `.` | (empty) |
| `..txt` | `.` | `.txt` |

Paths may be long (thousands of characters); the function is called on every file rotation, so keep it cheap.

=== CONTEXT ===
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

=== STUB ===
```cpp
static std::tuple<filename_t, filename_t> split_by_extension(const spdlog::filename_t &fname)
{
    // TODO: implement according to the specification
}
```
