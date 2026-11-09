You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `pattern_formatter::handle_flag_(flag, padding)`

## 1. Component overview

Part of spdlog's pattern formatter. While a pattern string such as `[%Y-%m-%d] [%-8l] %v` is compiled, every `%`-flag found in it is turned into a formatter object that later produces the text for that flag. `handle_flag_` receives the flag character (the character after the `%` and after an optional padding specification) together with the padding that was parsed for it, creates the matching formatter and appends it to the formatter list of the pattern formatter.

## 2. Functional requirements

Exactly one formatter object is appended to the end of the list (`formatters_`) per call; nothing else is modified and nothing already in the list is changed. Which formatter is created depends on `flag`; the formatter is constructed with `padding` unless noted.

| flag | formatter class |
|---|---|
| `+` | `full_formatter` |
| `n` | `name_formatter` |
| `l` | `level_formatter` |
| `L` | `short_level_formatter` |
| `t` | `t_formatter` |
| `v` | `v_formatter` |
| `a` | `a_formatter` |
| `A` | `A_formatter` |
| `b` and `h` | `b_formatter` |
| `B` | `B_formatter` |
| `c` | `c_formatter` |
| `C` | `C_formatter` |
| `Y` | `Y_formatter` |
| `D` and `x` | `D_formatter` |
| `m` | `m_formatter` |
| `d` | `d_formatter` |
| `H` | `H_formatter` |
| `I` | `I_formatter` |
| `M` | `M_formatter` |
| `S` | `S_formatter` |
| `e` | `e_formatter` |
| `f` | `f_formatter` |
| `F` | `F_formatter` |
| `E` | `E_formatter` |
| `p` | `p_formatter` |
| `r` | `r_formatter` |
| `R` | `R_formatter` |
| `T` and `X` | `T_formatter` |
| `z` | `z_formatter` |
| `P` | `pid_formatter` |
| `i` | `i_formatter` (because `SPDLOG_ENABLE_MESSAGE_COUNTER` is defined; without that macro `i` would be an unknown flag) |
| `^` | `color_start_formatter` |
| `$` | `color_stop_formatter` |
| `@` | `source_location_formatter` |
| `s` | `source_filename_formatter` |
| `#` | `source_linenum_formatter` |
| `!` | `source_funcname_formatter` |
| `%` | `ch_formatter` constructed with the character `'%'`; the padding is ignored, so `%%` prints one `%` |
| any other character | an `aggregate_formatter` holding the two characters `%` followed by `flag`, so an unknown flag is printed as it was written (for example `%y` prints `%y`, `%]` prints `%]`); the padding is ignored |

The flag characters are case sensitive (`a` and `A`, `b` and `B`, `m` and `M`, `d` and `D` are different flags). Whatever text the created formatter produces for a message (date parts, thread id, padding, colour range marks, ...) is that formatter's own behaviour and is not part of this function.

## 3. Input specification

- `flag`: any `char` (a printable character, including characters with no meaning such as `k`, `y`, `]`, a digit or a space).
- `padding`: a `details::padding_info` (width 0..128 and side left, right or center).

## 4. Output specification

No return value. The formatter list grows by exactly one element. No exceptions are thrown by this function.

## 5. Edge cases and constraints

When the finished pattern is applied to a message, the effect of each call is visible in the output, e.g. (UTC, 2017-07-14 02:40:00.123, thread id 77, logger `main`, level info, payload `hello`):

| call | output of that formatter |
|---|---|
| `handle_flag_('v', no padding)` | `hello` |
| `handle_flag_('l', width 8, right)` | `info    ` |
| `handle_flag_('x', no padding)` | `07/14/17` |
| `handle_flag_('X', no padding)` | `02:40:00` |
| `handle_flag_('t', width 3, left)` | ` 77` |
| `handle_flag_('%', width 9, left)` | `%` |
| `handle_flag_('y', width 9, left)` | `%y` |
| `handle_flag_('^', ...)` | no text (marks the start of the colour range) |

The function runs once for every flag when a pattern is compiled; keep it simple and allocation-light (one allocation per call).

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
spdlog::pattern_formatter::handle_padspec_( std :: string :: const_iterator & it , std :: string :: const_iterator end)
spdlog::pattern_formatter::pattern_formatter( pattern_time_type time_type = pattern_time_type :: local , std :: string eol = spdlog :: details :: os :: default_eol)
spdlog::pattern_formatter::pattern_formatter( std :: string pattern , pattern_time_type time_type = pattern_time_type :: local , std :: string eol = spdlog :: details :: os :: default_eol)
```

## Instance state (class `spdlog::pattern_formatter`)

The stub is a private member function of `class spdlog::pattern_formatter` (declared `final`, derived from `spdlog::formatter`). Members:

```cpp
std::string pattern_;                    // the pattern text given to the constructor
std::string eol_;                        // appended after every formatted message
pattern_time_type pattern_time_type_;    // local or utc
std::tm cached_tm_;
std::chrono::seconds last_log_secs_;
std::vector<std::unique_ptr<details::flag_formatter>> formatters_;   // the compiled pattern: formatters run in order by format()
```

`pattern_formatter::format(msg, dest)` runs every element of `formatters_` in order (each appends its text to `dest`) and then appends `eol_`. `compile_pattern_(pattern)`, `handle_padspec_(it, end)` and `handle_flag_(flag, padding)` (signatures listed above) are the members that build `formatters_`. `details::aggregate_formatter` is a flag formatter holding literal text: `add_ch(char)` appends one character to it and its `format` appends the stored text unchanged (default constructor, no padding).

## Types used by the stub

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

Every formatter class named in the specification is defined in the same file (see the list above) in namespace `spdlog::details`, and has a constructor taking a `details::padding_info` (except `ch_formatter`, whose constructor takes a `char`, and `aggregate_formatter`, see above). `details::make_unique<T>(args...)` creates a `std::unique_ptr<T>` (it is `std::make_unique` in C++14 and a local equivalent in C++11); a `unique_ptr<Derived>` converts to the vector's element type.

`SPDLOG_ENABLE_MESSAGE_COUNTER` is defined in this build (as in the library's test suite), so the `i` flag is active.

=== STUB ===
```cpp
void handle_flag_(char flag, details::padding_info padding)
{
    // TODO: implement according to the specification
}
```
