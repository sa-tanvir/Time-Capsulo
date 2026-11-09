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
