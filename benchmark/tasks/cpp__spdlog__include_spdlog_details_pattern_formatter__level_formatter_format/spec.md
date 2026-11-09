# Functional specification: `level_formatter::format(msg, tm_time, dest)`

## 1. Component overview

One of the flag formatters of spdlog's pattern formatter: it implements the `%l` flag of a log pattern, which prints the severity level of the message as a word. A pattern can request padding for the flag (`%8l`, `%-8l`, `%=8l`); the request is stored in the formatter object when it is created.

## 2. Functional requirements

Appends the textual name of `msg.level` to `dest` (existing content of `dest` is kept):

1. The names are `trace`, `debug`, `info`, `warning`, `error`, `critical` and `off` for the levels `trace`, `debug`, `info`, `warn`, `err`, `critical` and `off`.
2. If the formatter's padding is not enabled (width 0) the name is appended unchanged.
3. If padding is enabled, the name is padded with spaces up to the padding width and aligned according to the padding side; it is never truncated.

Padding (when enabled, i.e. the width is not 0): a field whose text has `n` characters is padded with spaces up to `width` characters. If `n >= width` nothing is added (the text is never truncated). Otherwise `width - n` spaces are added, according to the side:
- `left`: all spaces before the text (the text is right-aligned);
- `right`: all spaces after the text (the text is left-aligned);
- `center`: `(width - n) / 2` spaces (rounded down) before the text and the remaining spaces after it.
Examples (width 8, text `abc`): left `"     abc"`, right `"abc     "`, center `"  abc   "`; width 7, text `ab`, center: `"  ab   "`.

4. The `tm_time` argument and the other fields of the message are not used.

## 3. Input specification

- `msg`: a `log_msg` whose `level` is any of the seven `level_enum` values.
- `tm_time`: ignored.
- `dest`: a `fmt::memory_buffer`, possibly already containing text.
- The padding comes from the formatter's own padding member: width 0..128, side left, right or center.

## 4. Output specification

No return value. Only `dest` is extended, with the (padded) level name.

## 5. Edge cases and constraints

| level | padding | appended |
|---|---|---|
| info | none | `info` |
| warn | none | `warning` |
| info | width 8, left | `    info` |
| info | width 8, right | `info    ` |
| info | width 8, center | `  info  ` |
| off | width 4, center | `off ` |
| critical | width 3, left | `critical` |
| trace | width 6, center | `trace ` (one trailing space) |
