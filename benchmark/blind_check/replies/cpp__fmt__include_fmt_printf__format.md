```cpp
OutputIt basic_printf_context<OutputIt, Char>::format() {
  auto out = this->out();
  const Char* start = parse_ctx_.begin();
  const Char* end = parse_ctx_.end();
  auto it = start;
  while (it != end) {
    char c = static_cast<char>(*it++);
    if (c != '%') continue;
    if (it != end && *it == c) {
      out = std::copy(start, it, out);
      start = ++it;
      continue;
    }
    out = std::copy(start, it - 1, out);

    format_specs specs;
    specs.align = align::right;

    // Parse argument index, flags and width.
    unsigned arg_index = parse_header(it, end, specs);
    if (arg_index == 0) on_error("argument index out of range");

    // Parse precision.
    if (it != end && *it == '.') {
      ++it;
      c = it != end ? static_cast<char>(*it) : 0;
      if ('0' <= c && c <= '9') {
        specs.precision = parse_nonnegative_int(it, end, internal::error_handler());
      } else if (c == '*') {
        ++it;
        specs.precision = static_cast<int>(
            visit_format_arg(internal::printf_precision_handler(), get_arg()));
      } else {
        specs.precision = 0;
      }
    }

    format_arg arg = get_arg(arg_index);
    if (specs.alt && visit_format_arg(internal::is_zero_int(), arg))
      specs.alt = false;
    if (specs.fill[0] == '0') {
      if (arg.is_arithmetic())
        specs.align = align::numeric;
      else
        specs.fill[0] = ' ';
    }

    if (it == end) FMT_THROW(format_error("invalid type specifier"));

    // Parse length and convert the argument to the required type.
    c = static_cast<char>(*it++);
    char t = it != end ? static_cast<char>(*it) : 0;
    using internal::convert_arg;
    switch (c) {
    case 'h':
      if (t == 'h') {
        ++it;
        t = it != end ? static_cast<char>(*it) : 0;
        convert_arg<signed char>(arg, t);
      } else {
        convert_arg<short>(arg, t);
      }
      break;
    case 'l':
      if (t == 'l') {
        ++it;
        t = it != end ? static_cast<char>(*it) : 0;
        convert_arg<long long>(arg, t);
      } else {
        convert_arg<long>(arg, t);
      }
      break;
    case 'j':
      convert_arg<intmax_t>(arg, t);
      break;
    case 'z':
      convert_arg<std::size_t>(arg, t);
      break;
    case 't':
      convert_arg<std::ptrdiff_t>(arg, t);
      break;
    case 'L':
      // printf produces garbage when 'L' is omitted for long double, no
      // need to do the same.
      break;
    default:
      --it;
      convert_arg<void>(arg, c);
    }

    // Parse type.
    if (it == end) FMT_THROW(format_error("invalid format string"));
    specs.type = static_cast<char>(*it++);
    if (arg.is_integral()) {
      // Normalize type.
      switch (specs.type) {
      case 'i':
      case 'u':
        specs.type = 'd';
        break;
      case 'c':
        visit_format_arg(
            internal::char_converter<basic_printf_context>(arg), arg);
        break;
      }
    }

    start = it;

    // Format argument.
    out = visit_format_arg(ArgFormatter(out, specs, *this), arg);
  }
  out = std::copy(start, it, out);
  return out;
}
```
