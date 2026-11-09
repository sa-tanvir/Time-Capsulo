# Functional specification: `basic_printf_context<OutputIt, Char>::format()`

## 1. Component overview

The main loop of fmt's printf-compatible formatting (`fmt::sprintf`, `fmt::printf`). It walks the printf format string held by the context, copies literal text to the output, and for every conversion specification `%[N$][flags][width][.precision][length]type` it fetches the matching argument, converts it as printf would and writes it using the argument formatter. It returns the output iterator after all output.

## 2. Functional requirements

The format string is the range `[parse_ctx_.begin(), parse_ctx_.end())`. The function processes it from the start to the end and returns the final output iterator (`out()` after the last write).

1. **Literal text and escapes.** Everything outside a conversion is copied unchanged, in order. `%%` writes a single `%`. A format string without any `%` is copied as is.
2. **Conversion specification.** A `%` that is not followed by another `%` starts a specification with these parts, in order, all optional except the type:
   1. *Header*: argument index, flags and width, handled entirely by `parse_header`. Start from a fresh `format_specs` whose alignment is `align::right`. If `parse_header` returns the index 0 (from `%0$d`) the function reports the error `"argument index out of range"` with `on_error`.
   2. *Precision*: if the next character is `.`, it is consumed and: a run of decimal digits gives the precision (`parse_nonnegative_int` with a default `error_handler`, so a value above INT_MAX raises `"number is too big"`); `*` takes the precision from the next automatic argument through `printf_precision_handler` (a negative argument means precision 0, a non-integer argument raises `"precision is not integer"`); anything else (a lone `.`) means precision 0. Without a `.` the precision stays unset.
   3. *Argument*: the argument to format is fetched with `get_arg`: the one named by the index from the header, or the next automatic one. (This happens before the length and type are examined, so a missing argument is reported first, even when the format string ends in the middle of the specification.)
   4. *Adjustments from the flags*: if the `#` flag is set and the argument is an integer zero (use `is_zero_int`), the `#` flag is ignored. If the `0` flag was given (the header leaves the fill character `'0'`): for an arithmetic argument (integers, bool, char, floating point) the alignment becomes `align::numeric`; for any other argument (strings, pointers, custom types) the `0` flag is ignored and the fill is a space.
   5. *Length modifier*: `hh`, `h`, `l`, `ll`, `j`, `z`, `t` or `L`. For `hh`, `h`, `l`, `ll`, `j`, `z`, `t` an integer argument is converted with `convert_arg` to the matching type (`signed char`, `short`, `long`, `long long`, `intmax_t`, `std::size_t`, `std::ptrdiff_t`), passing the character that follows the modifier as the type. `L` has no effect. With no length modifier the argument is converted with `convert_arg` with `void`, passing the character at the current position as the type (the character is not consumed by this step).
   6. *Type*: the next character is the conversion type, which is consumed and stored in `specs.type`. If the format string ends right after a length modifier, the error `"invalid format string"` is thrown (`format_error`). If the argument is an integer, then `i` and `u` are normalised to `d`, and for `c` the argument is converted to a character with `char_converter`.
   7. The argument is written by applying a freshly constructed argument formatter (built from the output iterator, the finished specs and the context) to the argument through `visit_format_arg`; this validates the type character against the argument (an invalid combination, such as `%d` with a string or `%q`, raises `"invalid type specifier"` there) and applies width, precision, flags and alignment. Output continues after the specification.
3. **Premature end.** If the format string ends before a type character is found and no length modifier was read (for example `%5`, `%.` or a lone `%` at the end, with an argument available), the specification is invalid and `format_error("invalid type specifier")` is thrown. If the end follows a length modifier the error is `"invalid format string"` as in 2.6.
4. **Argument indexing.** Automatic (`%d`) and positional (`%1$d`) indexing must not be mixed within one format string: mixing raises `"cannot switch from manual to automatic argument indexing"` or `"cannot switch from automatic to manual argument indexing"` (these come from `get_arg`). A `*` width or precision uses the next automatic argument. Using more automatic conversions than arguments, or an index larger than the number of arguments, raises `"argument index out of range"`.
5. After the last conversion the remaining literal text is copied.

All errors are `format_error` exceptions (through `on_error`, `FMT_THROW`, or the helpers). Output written before an error is irrelevant to the caller.

## 3. Input specification

- State as described in the context: the format string (any length, possibly empty), the arguments, the output iterator.
- The argument formatter type `ArgFormatter` has the constructor and call protocol described in the context.

## 4. Output specification

Returns the output iterator after the whole format string was processed. All output (text and formatted arguments) has been written through it. Throws `format_error` for the cases above.

## 5. Edge cases and constraints

| format, arguments | result |
|---|---|
| `100%% sure` | `100% sure` |
| `%d`, 42 | `42` |
| `%5d`, 42 / `%-5d`, 42 | `   42` / `42   ` |
| `%05d`, -42 | `-0042` |
| `%0-5d`, 42 | `00042` (the `0` flag wins over `-` for numbers) |
| `%05s`, "ab" | `   ab` (the `0` flag is ignored for strings) |
| `%#x`, 0 | `0` (`#` ignored for zero) |
| `%.3s`, "hello" | `hel` |
| `%.5d`, 42 | `00042` |
| `%.s`, "abc" | `` (empty: precision 0) |
| `%*d`, 5, 42 / `%*d`, -5, 42 | `   42` / `42   ` |
| `%.*d`, 5, 42 / `%.*d`, -5, 42 | `00042` / `42` |
| `%2$d %1$s`, "a", 7 | `7 a` |
| `%1$s%2$s%1$s`, "abra", "cad" | `abracadabra` |
| `%hhd`, 300 / `%hd`, 70000 | `44` / `4464` |
| `%hhu`, -1 / `%hu`, -1 / `%u`, -1 | `255` / `65535` / `4294967295` |
| `%llu`, 18446744073709551615 | `18446744073709551615` |
| `%c`, 65 | `A` |
| `%i`, 7 | `7` |
| `%s`, null C string | `(null)` (written by the argument formatter) |
| `%d` (no arguments) / `%2$d`, 42 / `%0$d`, 42 | error `argument index out of range` |
| `%1$d%d`, 1, 2 | error `cannot switch from manual to automatic argument indexing` |
| `%d%1$d`, 1, 2 | error `cannot switch from automatic to manual argument indexing` |
| `%2147483648$d`, 42 / `%99999999999d`, 1 | error `number is too big` |
| `%*d`, 5.0, 42 | error `width is not integer` |
| `%.*d`, 5.0, 42 | error `precision is not integer` |
| `%5-5d`, 42 / `%q`, 1 / `%d`, "abc" | error `invalid type specifier` |
| `%l`, 1 / `%hh`, 1 | error `invalid format string` |
| `%5`, 1 | error `invalid type specifier` |
