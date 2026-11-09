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
