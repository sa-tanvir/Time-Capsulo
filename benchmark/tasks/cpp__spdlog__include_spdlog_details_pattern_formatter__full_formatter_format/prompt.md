You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `full_formatter::format(msg, tm_time, dest)`

## 1. Component overview

The default log-line formatter of spdlog (the `%+` flag; equal to the pattern `[%Y-%m-%d %H:%M:%S.%e] [%n] [%l] %v`, plus an optional source location). It writes one complete log line, without end-of-line, into the output buffer, and records where the level name sits in the output so that colouring sinks can colour it.

## 2. Functional requirements

`tm_time` is the broken-down calendar time (in the pattern's time zone) that corresponds to `msg.time`; the date and time of day are taken from it, while the milliseconds come from `msg.time`. The function appends the following pieces to `dest`, in this order, after whatever `dest` already contains:

1. A timestamp: `[` year `-` month `-` day `' '` hour `:` minute `:` second `.` millis `]` and a space, where
   - year is `tm_year + 1900` in plain decimal (no padding);
   - month (`tm_mon + 1`), day (`tm_mday`), hour, minute and second are written with at least two digits (zero-padded);
   - millis is the sub-second part of `msg.time` truncated to whole milliseconds, written with at least three digits (zero-padded, 0..999).
2. If the logger name is not empty: `[` name `]` and a space. With an empty name this part is omitted completely.
3. `[` level-name `]` and a space, where level-name is the textual name of `msg.level` (`trace`, `debug`, `info`, `warning`, `error`, `critical`, `off`). While doing so, the function sets `msg.color_range_start` to the size of `dest` just before the level name is appended and `msg.color_range_end` to the size of `dest` just after it (absolute offsets in `dest`, i.e. they include any text that was in `dest` before the call).
4. If the message has a source location (`msg.source` is not empty, i.e. its `line` is non-zero): `[` filename `:` line `]` and a space, where line is a plain decimal number. The function name of the location is not printed.
5. The message text `msg.payload`, unchanged.

The padding given to the formatter is not used. No end-of-line is appended. `msg` is otherwise not modified.

## 3. Input specification

- `msg`: any valid `log_msg` as described in the context (payload may be empty or long, name may be empty).
- `tm_time`: a valid `std::tm` consistent with `msg.time`; years 1970..2036 occur.
- `dest`: a `fmt::memory_buffer`, possibly non-empty.

## 4. Output specification

No return value. `dest` is extended with the text above; `msg.color_range_start` and `msg.color_range_end` are updated.

## 5. Edge cases and constraints

Examples (time 2017-07-14 02:40:00 UTC plus 123 ms, `dest` initially empty):

| logger name | level | source | payload | appended text | colour range |
|---|---|---|---|---|---|
| `main` | info | none | `hello` | `[2017-07-14 02:40:00.123] [main] [info] hello` | 34, 38 |
| (empty) | error | `a.cpp`, line 42 | `hello` | `[2017-07-14 02:40:00.123] [error] [a.cpp:42] hello` | 27, 32 |
| `main` | warn | `a.cpp`, line 42 | `hello` | `[2017-07-14 02:40:00.123] [main] [warning] [a.cpp:42] hello` | 34, 41 |
| `main` | off | none | `hello` | `[2017-07-14 02:40:00.005] [main] [off] hello` (millis 5 ms) | 34, 37 |

The function runs once per log message and must be fast: no heap allocation beyond growth of `dest`,.

=== CONTEXT ===
# Context for the function to implement

- **Language:** cpp
- **File:** `include/spdlog/details/pattern_formatter.h`

## Imports / includes available in this file

```
#include "spdlog/details/fmt_helper.h"
#include "spdlog/details/log_msg.h"
#include "spdlog/details/os.h"
#include "spdlog/fmt/fmt.h"
#include "spdlog/formatter.h"
#include <array>
#include <chrono>
#include <ctime>
#include <cctype>
#include <memory>
#include <mutex>
#include <string>
#include <thread>
#include <utility>
#include <vector>
```

## Other functions defined in the same file (signatures only; you may call them)

```
spdlog::details::A_formatter::A_formatter( padding_info padinfo)
spdlog::details::A_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::B_formatter::B_formatter( padding_info padinfo)
spdlog::details::B_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::C_formatter::C_formatter( padding_info padinfo)
spdlog::details::C_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::D_formatter::D_formatter( padding_info padinfo)
spdlog::details::D_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::E_formatter::E_formatter( padding_info padinfo)
spdlog::details::E_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::F_formatter::F_formatter( padding_info padinfo)
spdlog::details::F_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::H_formatter::H_formatter( padding_info padinfo)
spdlog::details::H_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::I_formatter::I_formatter( padding_info padinfo)
spdlog::details::I_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::M_formatter::M_formatter( padding_info padinfo)
spdlog::details::M_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::R_formatter::R_formatter( padding_info padinfo)
spdlog::details::R_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::S_formatter::S_formatter( padding_info padinfo)
spdlog::details::S_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::T_formatter::T_formatter( padding_info padinfo)
spdlog::details::T_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::Y_formatter::Y_formatter( padding_info padinfo)
spdlog::details::Y_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::a_formatter::a_formatter( padding_info padinfo)
spdlog::details::a_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::aggregate_formatter::add_ch( char ch)
spdlog::details::aggregate_formatter::format( const details :: log_msg & , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::ampm( const tm & t)
spdlog::details::b_formatter::b_formatter( padding_info padinfo)
spdlog::details::b_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::c_formatter::c_formatter( padding_info padinfo)
spdlog::details::c_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::ch_formatter::ch_formatter( char ch)
spdlog::details::ch_formatter::format( const details :: log_msg & , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::color_start_formatter::color_start_formatter( padding_info padinfo)
spdlog::details::color_start_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::color_stop_formatter::color_stop_formatter( padding_info padinfo)
spdlog::details::color_stop_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::d_formatter::d_formatter( padding_info padinfo)
spdlog::details::d_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::e_formatter::e_formatter( padding_info padinfo)
spdlog::details::e_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::f_formatter::f_formatter( padding_info padinfo)
spdlog::details::f_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::flag_formatter::flag_formatter( padding_info padinfo)
spdlog::details::full_formatter::full_formatter( padding_info padinfo)
spdlog::details::i_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::i_formatter::i_formatter( padding_info padinfo)
spdlog::details::level_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::level_formatter::level_formatter( padding_info padinfo)
spdlog::details::m_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::m_formatter::m_formatter( padding_info padinfo)
spdlog::details::name_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::name_formatter::name_formatter( padding_info padinfo)
spdlog::details::p_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::p_formatter::p_formatter( padding_info padinfo)
spdlog::details::padding_info::enabled() const
spdlog::details::padding_info::padding_info( size_t width , padding_info :: pad_side side)
spdlog::details::pid_formatter::format( const details :: log_msg & , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::pid_formatter::pid_formatter( padding_info padinfo)
spdlog::details::r_formatter::format( const details :: log_msg & , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::r_formatter::r_formatter( padding_info padinfo)
spdlog::details::scoped_pad::pad_it( size_t count)
spdlog::details::scoped_pad::scoped_pad( size_t wrapped_size , padding_info & padinfo , fmt :: memory_buffer & dest)
spdlog::details::scoped_pad::scoped_pad( spdlog :: string_view_t txt , padding_info & padinfo , fmt :: memory_buffer & dest)
spdlog::details::scoped_pad::~scoped_pad()
spdlog::details::short_level_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::short_level_formatter::short_level_formatter( padding_info padinfo)
spdlog::details::source_filename_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::source_filename_formatter::source_filename_formatter( padding_info padinfo)
spdlog::details::source_funcname_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::source_funcname_formatter::source_funcname_formatter( padding_info padinfo)
spdlog::details::source_linenum_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::source_linenum_formatter::source_linenum_formatter( padding_info padinfo)
spdlog::details::source_location_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::source_location_formatter::source_location_formatter( padding_info padinfo)
spdlog::details::t_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::t_formatter::t_formatter( padding_info padinfo)
spdlog::details::to12h( const tm & t)
spdlog::details::v_formatter::format( const details :: log_msg & msg , const std :: tm & , fmt :: memory_buffer & dest)
spdlog::details::v_formatter::v_formatter( padding_info padinfo)
spdlog::details::z_formatter::format( const details :: log_msg & msg , const std :: tm & tm_time , fmt :: memory_buffer & dest)
spdlog::details::z_formatter::get_cached_offset( const log_msg & msg , const std :: tm & tm_time)
spdlog::details::z_formatter::z_formatter( padding_info padinfo)
spdlog::pattern_formatter::clone() const
spdlog::pattern_formatter::compile_pattern_( const std :: string & pattern)
spdlog::pattern_formatter::format( const details :: log_msg & msg , fmt :: memory_buffer & dest)
spdlog::pattern_formatter::get_time_( const details :: log_msg & msg)
spdlog::pattern_formatter::handle_flag_( char flag , details :: padding_info padding)
spdlog::pattern_formatter::handle_padspec_( std :: string :: const_iterator & it , std :: string :: const_iterator end)
spdlog::pattern_formatter::pattern_formatter( pattern_time_type time_type = pattern_time_type :: local , std :: string eol = spdlog :: details :: os :: default_eol)
spdlog::pattern_formatter::pattern_formatter( std :: string pattern , pattern_time_type time_type = pattern_time_type :: local , std :: string eol = spdlog :: details :: os :: default_eol)
```

## Instance state and types

The stub is the `format` member (an override) of `class spdlog::details::full_formatter final : public flag_formatter`, the formatter behind the default pattern `[%Y-%m-%d %H:%M:%S.%e] [%n] [%l] %v` (flag `%+`). It is constructed with `full_formatter(padding_info padinfo)`; the padding is ignored by this formatter. Private members of the class:

```cpp
std::chrono::seconds cache_timestamp_{0};                    // second of the date/time text cached last
fmt::basic_memory_buffer<char, 128> cached_datetime_;        // cached "[YYYY-MM-DD HH:MM:SS." text
```
(The date/time prefix of consecutive messages that fall into the same second can be cached in these members; they are optional helpers, the observable output is what the specification below describes.)

Build configuration: neither `SPDLOG_NO_DATETIME` nor `SPDLOG_NO_NAME` is defined (all parts below are present). Types and helpers:

```cpp
// spdlog/common.h
using log_clock = std::chrono::system_clock;
struct source_loc { const char *filename; uint32_t line; const char *funcname; bool empty() const; /* line == 0 */ };
namespace level { string_view_t &to_string_view(level_enum l); }     // "trace","debug","info","warning","error","critical","off"
// spdlog/details/log_msg.h
struct log_msg {
    const std::string *logger_name;        // never null, may be empty
    level::level_enum level;
    log_clock::time_point time;            // microsecond/nanosecond resolution, at or after the Unix epoch
    mutable size_t color_range_start;      // to be set by this function (see below)
    mutable size_t color_range_end;
    source_loc source;
    const string_view_t payload;           // the message text
};
// spdlog/details/fmt_helper.h (all in namespace spdlog::details::fmt_helper): see the list above, in particular
//   append_int(T n, buf), pad2(int n, buf), pad3(T n, buf), append_string_view(view, buf), append_buf(buf, dest),
//   time_fraction<ToDuration>(const log_clock::time_point &tp)   // sub-second part of tp as ToDuration (e.g. std::chrono::milliseconds)
```
`dest` is a `fmt::memory_buffer`; `push_back(char)` appends one character.

=== STUB ===
```cpp
void format(const details::log_msg &msg, const std::tm &tm_time, fmt::memory_buffer &dest) override
{
    // TODO: implement according to the specification
}
```
