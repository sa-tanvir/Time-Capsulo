You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `parse_chrono_format(begin, end, handler)`

## 1. Component overview

Part of fmt's `<chrono>` support. It parses a `strftime`/`put_time`-like format string such as `%H:%M:%S` or `elapsed: %Q%q`, splitting it into literal text and conversion specifiers, and tells a handler object what it found through callbacks. It is used both to validate a format string and to format a time value. It returns the position where parsing stopped.

## 2. Functional requirements

The range `[begin, end)` is processed from left to right. Parsing stops at the end of the range or at the first `}` that is found while scanning literal text (the closing brace of the enclosing replacement field); the function returns a pointer to that position (`end` or the `}`).

1. **Literal text.** Every character other than `%` is literal. A maximal run of literal characters that precedes a conversion (or the stopping position) is reported with one call `handler.on_text(first, last)`, where `[first, last)` points into the input range. No call is made for an empty run. Text is flushed immediately before the handler is notified about a conversion, and the remaining text at the stopping position is flushed at the end.
2. **Conversions.** `%` followed by a character selects a conversion; the handler is notified with the call below, and parsing continues right after the conversion:

| spec | call | spec | call |
|---|---|---|---|
| `%a` | `on_abbr_weekday()` | `%p` | `on_am_pm()` |
| `%A` | `on_full_weekday()` | `%Q` | `on_duration_value()` |
| `%w` | `on_dec0_weekday(standard)` | `%q` | `on_duration_unit()` |
| `%u` | `on_dec1_weekday(standard)` | `%z` | `on_utc_offset()` |
| `%b` | `on_abbr_month()` | `%Z` | `on_tz_name()` |
| `%B` | `on_full_month()` | `%c` | `on_datetime(standard)` |
| `%H` | `on_24_hour(standard)` | `%x` | `on_loc_date(standard)` |
| `%I` | `on_12_hour(standard)` | `%X` | `on_loc_time(standard)` |
| `%M` | `on_minute(standard)` | `%D` | `on_us_date()` |
| `%S` | `on_second(standard)` | `%F` | `on_iso_date()` |
| `%r` | `on_12_hour_time()` | `%R` | `on_24_hour_time()` |
| `%T` | `on_iso_time()` | | |

3. **Escapes.** `%%` yields a literal percent: `on_text` is called with the one-character range consisting of the second `%` (a pointer into the input). `%n` calls `on_text` with a one-character range holding a newline `"\n"`, and `%t` with a one-character range holding a tab `"\t"` (these two ranges do not point into the input). Before them, pending literal text is flushed as in rule 1.
4. **Alternative representations.** `%E` must be followed by `c`, `x` or `X`, giving `on_datetime(alternative)`, `on_loc_date(alternative)` or `on_loc_time(alternative)`. `%O` must be followed by one of `w`, `u`, `H`, `I`, `M`, `S`, giving `on_dec0_weekday`, `on_dec1_weekday`, `on_24_hour`, `on_12_hour`, `on_minute`, `on_second` with `alternative`.
5. **Errors.** The function throws `format_error` with the message `"invalid format"` when: the format ends right after a `%`; the character after `%` is not one of the above (including `}` and `Y`); `%E` or `%O` is at the end of the range or is followed by a character not allowed for it. Callbacks made before the error was detected stay made.
6. Because the scan for literal text stops at `}`, a `}` in literal text ends the parse (text before it is flushed first), while a `}` directly after `%` is an invalid conversion (rule 5).

## 3. Input specification

- `begin`, `end`: `const Char*` pointers (`Char` is `char` or `wchar_t`), `begin <= end`; the range may be empty.
- `handler`: as described in the context.

## 4. Output specification

Returns the pointer to the position where parsing stopped (`end`, or the `}` that terminated it). The handler receives the callbacks in input order. Throws `format_error("invalid format")` as above.

## 5. Edge cases and constraints

| input | callbacks | return (offset) |
|---|---|---|
| `` (empty) | none | 0 |
| `abc` | `on_text("abc")` | 3 |
| `%H:%M` | `on_24_hour(std)`, `on_text(":")`, `on_minute(std)` | 5 |
| `a%%b` | `on_text("a")`, `on_text("%")`, `on_text("b")` | 4 |
| `x%Hy}z` | `on_text("x")`, `on_24_hour(std)`, `on_text("y")` | 5 (the `}`) |
| `}` | none | 0 |
| `%OS` | `on_second(alternative)` | 3 |
| `%` , `%Y` , `%Ey` , `%Oz` , `%E` , `%}` | throws `format_error("invalid format")` | |
| `ab%` | `on_text("ab")` is made, then throws | |

=== CONTEXT ===
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

=== STUB ===
```cpp
FMT_CONSTEXPR const Char* parse_chrono_format(const Char* begin,
                                              const Char* end,
                                              Handler&& handler) {
    // TODO: implement according to the specification
}
```
