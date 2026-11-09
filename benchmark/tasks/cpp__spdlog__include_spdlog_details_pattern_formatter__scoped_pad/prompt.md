You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `scoped_pad(wrapped_size, padinfo, dest)` (constructor)

## 1. Component overview

`scoped_pad` is a small RAII helper of spdlog's pattern formatter. A formatter creates a `scoped_pad` for a field of known length, then appends the field text to the buffer, and lets the object go out of scope. The constructor writes the padding that must come before the text and records how many padding characters must come after it; the destructor writes those. The result is that the field occupies at least `padinfo.width_` characters, aligned according to `padinfo.side_`.

## 2. Functional requirements

Let `width = padinfo.width_`, `side = padinfo.side_` and `n = wrapped_size` (the number of characters the caller is going to append after construction).

1. If `width <= n`, no padding is needed: nothing is appended to `dest` and nothing is left for the destructor.
2. Otherwise let `total = width - n`:
   - `side == left`: append `total` spaces to `dest` now; nothing is left for the destructor (the text ends up right-aligned).
   - `side == right`: append nothing now; the destructor has to append `total` spaces (the text ends up left-aligned).
   - `side == center`: append `total / 2` spaces (integer division, rounded down) now; the destructor has to append the remaining `total - total / 2` spaces (so when `total` is odd, the extra space goes on the right).
3. The number of spaces the destructor appends is held in the member that the destructor reads (see the instance state); every path through the constructor must leave it set to the correct value, including 0.

The constructor only appends spaces (`' '`) to `dest`; it does not read or modify anything already in `dest`. It does not modify `padinfo`.

## 3. Input specification

- `wrapped_size`: `size_t`, from 0 to a few thousand.
- `padinfo`: a `padding_info` with `width_` between 0 and 128 and `side_` one of `left`, `right`, `center`.
- `dest`: a `fmt::memory_buffer` that may already contain text.

## 4. Output specification

No return value. After the constructor, `dest` has the leading padding appended; after the whole object's lifetime (constructor, caller's text, destructor) the buffer holds `[leading spaces][text][trailing spaces]`.

## 5. Edge cases and constraints

| width | side | n | leading spaces (constructor) | trailing spaces (destructor) |
|---|---|---|---|---|
| 8 | left | 4 | 4 | 0 |
| 8 | right | 4 | 0 | 4 |
| 8 | center | 4 | 2 | 2 |
| 7 | center | 2 | 2 | 3 |
| 3 | left | 14 | 0 | 0 |
| 4 | center | 4 | 0 | 0 |
| 0 | any | 0 | 0 | 0 |
| 5 | center | 0 | 2 | 3 |

The constructor is invoked for every padded field of every log line, so it must be cheap.

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
spdlog::details::full_formatter::format( const details :: log_msg & msg , const std :: tm & tm_time , fmt :: memory_buffer & dest)
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

The stub is the first constructor (the `size_t wrapped_size` one) of `class spdlog::details::scoped_pad`, written as in the stub with its member initialiser list (`padinfo_(padinfo)`, `dest_(dest)`) which is part of the stub text you must keep. Members, helpers and related types:

```cpp
namespace spdlog {            // all of the following lives in namespace spdlog::details unless stated
using string_view_t = fmt::string_view;     // spdlog::string_view_t
namespace details {

struct padding_info {                       // how a field is padded
    enum pad_side { left, right, center };
    padding_info() = default;                                   // width_ == 0, side_ == left
    padding_info(size_t width, padding_info::pad_side side);
    bool enabled() const { return width_ != 0; }                // padding is only requested when the width is non-zero
    const size_t width_ = 0;                                    // minimum field width in characters
    const pad_side side_ = left;
};

class scoped_pad {                          // pads the text that is appended to `dest` while it is alive
public:
    scoped_pad(size_t wrapped_size, padding_info &padinfo, fmt::memory_buffer &dest);       // writes the padding that goes BEFORE the text
    scoped_pad(spdlog::string_view_t txt, padding_info &padinfo, fmt::memory_buffer &dest); // same, wrapped_size = txt.size()
    ~scoped_pad();                          // writes the padding that goes AFTER the text (total_pad_ spaces, if non-zero)
private:
    void pad_it(size_t count);              // appends `count` spaces to dest_ (count <= 128)
    const padding_info &padinfo_;
    fmt::memory_buffer &dest_;
    size_t total_pad_;                      // number of spaces the destructor still has to append
};

class flag_formatter {                      // base class of every pattern flag formatter
public:
    explicit flag_formatter(padding_info padinfo);
    virtual ~flag_formatter() = default;
    virtual void format(const details::log_msg &msg, const std::tm &tm_time, fmt::memory_buffer &dest) = 0;
protected:
    padding_info padinfo_;                  // the padding requested for this flag
};

struct log_msg {                            // one log record (relevant members)
    const std::string *logger_name;         // never null
    level::level_enum level;                // level::trace(0) .. level::off(6)
    log_clock::time_point time;             // std::chrono::system_clock time point
    size_t thread_id;
    size_t msg_id;
    mutable size_t color_range_start;       // offsets into the formatted output
    mutable size_t color_range_end;
    source_loc source;                      // source.filename, source.line (0 == "no location"), source.funcname; source.empty()
    const string_view_t payload;            // the message text
};
}}
```

The destructor appends `total_pad_` spaces through `pad_it` when `total_pad_` is non-zero, so the constructor must leave `total_pad_` set to the number of spaces that belong after the text (0 if none).

=== STUB ===
```cpp
scoped_pad(size_t wrapped_size, padding_info &padinfo, fmt::memory_buffer &dest)
    : padinfo_(padinfo)
    , dest_(dest)
{
    // TODO: implement according to the specification
}
```
