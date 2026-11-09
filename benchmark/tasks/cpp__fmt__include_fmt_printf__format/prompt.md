You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/printf.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { ... } }`
- **Enclosing scope:** the stub is the out-of-class definition of the member function template `basic_printf_context<OutputIt, Char>::format()`. Keep the signature exactly as in the stub.

## Declaration lines preceding the stub

These two lines stand directly above the stub in the source file and are NOT part of your answer (do not repeat them):

```
template <typename OutputIt, typename Char>
template <typename ArgFormatter>
```

## Instance state (class `basic_printf_context<OutputIt, Char>`)

```
template <typename OutputIt, typename Char> class basic_printf_context {
 public:
  using char_type = Char;
  using format_arg = basic_format_arg<basic_printf_context>;
 private:
  using format_specs = basic_format_specs<char_type>;

  OutputIt out_;                                   // output iterator (a back_insert_iterator or a truncating iterator)
  basic_format_args<basic_printf_context> args_;   // the arguments
  basic_format_parse_context<Char> parse_ctx_;     // holds the format string [begin(), end()) and the argument-indexing state

  // Returns the argument with the given 1-based index or, if arg_index is the maximum unsigned value, the next argument in
  // automatic order. Throws format_error "argument index out of range" when there is no such argument and
  // "cannot switch from manual to automatic argument indexing" / "cannot switch from automatic to manual argument indexing"
  // when the two indexing modes are mixed.
  format_arg get_arg(unsigned arg_index = internal::max_value<unsigned>());

  // Parses, starting at `it`, an optional argument index ("N$"), the flags (- + 0 space #) and the width (digits or '*', where
  // '*' takes the next argument), updating specs (align, sign, fill[0] (set to '0' by the 0 flag), alt, width) and advancing `it`.
  // Returns the 1-based argument index, or the maximum unsigned value when no index was given (0 is returned for "0$").
  unsigned parse_header(const Char*& it, const Char* end, format_specs& specs);

 public:
  OutputIt out();                       // the current output iterator
  void advance_to(OutputIt it);         // sets the output iterator
  void on_error(const char* message);   // throws format_error(message)

  template <typename ArgFormatter = printf_arg_formatter<buffer_range<Char>>>
  OutputIt format();                    // <-- the stub
};
```

## Types and helpers visible to the function

```
template <typename Char> struct basic_format_specs {   // fields used here
  int width;               // minimum field width (0 = none)
  int precision;           // -1 = none
  char type;               // conversion type character (0 = none)
  align_t align : 4;       // align::none, left, right, center, numeric
  sign_t sign : 3;         // sign::none, minus, plus, space
  bool alt : 1;            // '#'
  Char fill[...];          // fill[0] is the fill character (default ' ')
};

basic_format_arg<Context>: .is_arithmetic() (true for integers, bool, char and floating point), .is_integral() (integers, bool, char)

template <typename Visitor, typename Context> auto visit_format_arg(Visitor&& vis, const basic_format_arg<Context>& arg);
    // calls vis(value) with the argument's actual value

template <typename Char, typename ErrorHandler>
int parse_nonnegative_int(const Char*& begin, const Char* end, ErrorHandler&& eh);
    // parses decimal digits (precondition: *begin is a digit), advances begin, calls eh.on_error("number is too big") if > INT_MAX
internal::error_handler: a default constructible handler whose on_error(message) throws format_error(message)

internal::printf_precision_handler: visitor; operator()(integer) returns max(value, 0) as int (throws format_error "number is too big"
    if the integer does not fit in int); operator()(non-integer) throws format_error("precision is not integer")
internal::is_zero_int: visitor returning true iff the argument is an integer (or bool/char) equal to zero
template <typename T, typename Context, typename Char> void internal::convert_arg(basic_format_arg<Context>& arg, Char type);
    // Converts an integer argument in place for printf: to type T first (truncation/sign change, e.g. T = signed char turns 300 into 44,
    // T = short turns 70000 into 4464), then to the signed or unsigned print type: signed when `type` is 'd' or 'i', unsigned otherwise.
    // T = void keeps the argument's own width and only chooses signed/unsigned from `type`. Non-integer arguments are unchanged.
template <typename Context> class internal::char_converter {   // visitor: converts an integer argument to the character type in place
  explicit char_converter(basic_format_arg<Context>& arg);
};

ArgFormatter: constructed as ArgFormatter(out, specs, *this); calling visit_format_arg(that formatter, arg) writes the argument
    according to specs (width, precision, flags, alignment, type) to the output iterator and returns the new output iterator.
    It throws format_error "invalid type specifier" for a type character that is not valid for the argument.
```

`FMT_THROW(x)` throws `x`; `format_error(const char*)` is the library exception class. `std::copy` is available.

## Caller (for orientation only)

```
// internal::printf(buffer<Char>& buf, basic_string_view<Char> format, basic_format_args<Context> args):
//     Context(std::back_inserter(buf), format, args).format();
// fmt::sprintf("%d", 42) goes through it.
```

=== STUB ===
```cpp
OutputIt basic_printf_context<OutputIt, Char>::format() {
    // TODO: implement according to the specification
}
```
