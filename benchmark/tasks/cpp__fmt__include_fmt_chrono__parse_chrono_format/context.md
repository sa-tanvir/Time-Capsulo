# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/chrono.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`

## Includes available

```
#include "format.h"
#include <chrono>
#include <ctime>
#include <locale>
#include <sstream>
```

## Declaration line preceding the stub

The following line stands directly above the stub in the source file and is NOT part of your answer (do not repeat it):

```
template <typename Char, typename Handler>
```

`FMT_CONSTEXPR` is a macro for `constexpr` (C++14 and later) or nothing (C++11); keep it as in the stub. `FMT_THROW(x)` is a macro that throws `x` (exceptions are enabled).

## Types used

```
enum class numeric_system {
  standard,
  alternative   // "alternative numeric system", selected by the E and O modifiers
};

class format_error : public std::runtime_error {
 public:
  explicit format_error(const char* message);
  explicit format_error(const std::string& message);
};
```

## The Handler concept

`Handler` is a user supplied type (the argument is a forwarding reference). It provides these member functions, all returning `void`:

```
template <typename Char> void on_text(const Char* begin, const Char* end);   // literal text [begin, end)
on_abbr_weekday();  on_full_weekday();  on_abbr_month();  on_full_month();
on_us_date();  on_iso_date();  on_12_hour_time();  on_24_hour_time();  on_iso_time();
on_am_pm();  on_duration_value();  on_duration_unit();  on_utc_offset();  on_tz_name();
on_dec0_weekday(numeric_system);  on_dec1_weekday(numeric_system);
on_24_hour(numeric_system);  on_12_hour(numeric_system);  on_minute(numeric_system);  on_second(numeric_system);
on_datetime(numeric_system);  on_loc_date(numeric_system);  on_loc_time(numeric_system);
```

## Caller (for orientation only)

```
// chrono formatter::do_parse: it = internal::parse_chrono_format(it, end, internal::chrono_format_checker());
// internal::chrono_formatter::format: parse_chrono_format(format_str.begin(), format_str.end(), *this);
```
