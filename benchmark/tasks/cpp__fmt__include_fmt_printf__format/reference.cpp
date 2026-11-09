OutputIt basic_printf_context<OutputIt, Char>::format() {
  auto out = this->out();
  const Char* start = parse_ctx_.begin();
  const Char* end = parse_ctx_.end();
  auto it = start;
  while (it != end) {
    char_type c = *it++;
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
      c = it != end ? *it : 0;
      if ('0' <= c && c <= '9') {
        internal::error_handler eh;
        specs.precision = static_cast<int>(parse_nonnegative_int(it, end, eh));
      } else if (c == '*') {
        ++it;
        specs.precision =
            visit_format_arg(internal::printf_precision_handler(), get_arg());
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
        specs.fill[0] = ' ';  // Ignore '0' flag for non-numeric types.
    }

    // Parse length and convert the argument to the required type.
    c = it != end ? *it++ : 0;
    char_type t = it != end ? *it : 0;
    using internal::convert_arg;
    switch (c) {
    case 'h':
      if (t == 'h') {
        ++it;
        t = it != end ? *it : 0;
        convert_arg<signed char>(arg, t);
      } else {
        convert_arg<short>(arg, t);
      }
      break;
    case 'l':
      if (t == 'l') {
        ++it;
        t = it != end ? *it : 0;
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
        visit_format_arg(internal::char_converter<basic_printf_context>(arg),
                         arg);
        break;
      }
    }

    start = it;

    // Format argument.
    visit_format_arg(ArgFormatter(out, specs, *this), arg);
  }
  return std::copy(start, it, out);
}
