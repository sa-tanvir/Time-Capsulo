# Functional specification: `name_formatter::format(msg, tm_time, dest)`

## 1. Component overview

One of the flag formatters of spdlog's pattern formatter: it implements the `%n` flag of a log pattern, which prints the name of the logger that produced the message. A log pattern may request padding for the flag (for example `%10n`, `%-10n`, `%=10n`); the padding request is stored in the formatter object when it is created.

## 2. Functional requirements

Appends the logger name (`*msg.logger_name`) to `dest` (existing content of `dest` is kept):

1. If the formatter's padding is not enabled (its width is 0), the name is appended unchanged.
2. If padding is enabled, the name is padded with spaces up to the padding width and aligned according to the padding side. The name is never truncated or shortened, even when it is longer than the width (then no spaces are added).

Padding (when enabled, i.e. the width is not 0): a field whose text has `n` characters is padded with spaces up to `width` characters. If `n >= width` nothing is added (the text is never truncated). Otherwise `width - n` spaces are added, according to the side:
- `left`: all spaces before the text (the text is right-aligned);
- `right`: all spaces after the text (the text is left-aligned);
- `center`: `(width - n) / 2` spaces (rounded down) before the text and the remaining spaces after it.
Examples (width 8, text `abc`): left `"     abc"`, right `"abc     "`, center `"  abc   "`; width 7, text `ab`, center: `"  ab   "`.

3. The name may be empty: without padding nothing is appended, with padding only spaces (`width` of them) are appended.
4. The `tm_time` argument and the other fields of the message are not used.

## 3. Input specification

- `msg`: a `log_msg` whose `logger_name` points to a valid `std::string` (may be empty, any length).
- `tm_time`: ignored.
- `dest`: a `fmt::memory_buffer`, possibly already containing text.
- The padding comes from the formatter's own padding member: width 0..128, side left, right or center.

## 4. Output specification

No return value. Only `dest` is extended, with the (padded) logger name.

## 5. Edge cases and constraints

| name | padding | appended |
|---|---|---|
| `main` | none | `main` |
| `pattern_tester` | width 3, any side | `pattern_tester` |
| `abc` | width 8, left | `     abc` |
| `abc` | width 8, right | `abc     ` |
| `abc` | width 8, center | `  abc   ` |
| `ab` | width 7, center | `  ab   ` |
| (empty) | width 4, right | four spaces |
| (empty) | none | nothing |
