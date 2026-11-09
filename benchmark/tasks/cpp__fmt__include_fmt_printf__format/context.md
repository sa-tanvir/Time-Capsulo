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
