FMT_CONSTEXPR const Char* parse_align(const Char* begin, const Char* end,
                                      Handler&& handler) {
  FMT_ASSERT(begin != end, "");
  auto align = align::none;
  int i = 0;
  if (begin + 1 != end) ++i;
  do {
    switch (static_cast<char>(begin[i])) {
    case '<':
      align = align::left;
      break;
    case '>':
      align = align::right;
      break;
#if FMT_NUMERIC_ALIGN
    case '=':
      align = align::numeric;
      break;
#endif
    case '^':
      align = align::center;
      break;
    }
    if (align != align::none) {
      if (i > 0) {
        auto c = *begin;
        if (c == '{')
          return handler.on_error("invalid fill character '{'"), begin;
        begin += 2;
        handler.on_fill(c);
      } else
        ++begin;
      handler.on_align(align);
      break;
    }
  } while (i-- > 0);
  return begin;
}
