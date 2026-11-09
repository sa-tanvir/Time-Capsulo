```cpp
FMT_CONSTEXPR const Char* parse_align(const Char* begin, const Char* end,
                                      Handler&& handler) {
  FMT_ASSERT(begin != end, "");
  align_t align = align::none;
  auto to_align = [](char c) -> align_t {
    switch (c) {
    case '<': return align::left;
    case '>': return align::right;
    case '^': return align::center;
    case '=': return align::numeric;
    }
    return align::none;
  };
  if (end - begin > 1) {
    align = to_align(static_cast<char>(begin[1]));
    if (align != align::none) {
      if (*begin == '{') {
        handler.on_error("invalid fill character '{'");
        return begin;
      }
      handler.on_fill(*begin);
      handler.on_align(align);
      return begin + 2;
    }
  }
  align = to_align(static_cast<char>(*begin));
  if (align != align::none) {
    handler.on_align(align);
    return begin + 1;
  }
  return begin;
}
```
