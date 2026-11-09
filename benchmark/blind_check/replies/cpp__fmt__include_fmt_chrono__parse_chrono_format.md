```cpp
FMT_CONSTEXPR const Char* parse_chrono_format(const Char* begin,
                                              const Char* end,
                                              Handler&& handler) {
  auto ptr = begin;
  while (ptr != end) {
    auto c = *ptr;
    if (c == '}') break;
    if (c != '%') {
      ++ptr;
      continue;
    }
    if (begin != ptr) handler.on_text(begin, ptr);
    ++ptr;  // consume '%'
    if (ptr == end) FMT_THROW(format_error("invalid format"));
    c = *ptr++;
    switch (c) {
    case '%':
      handler.on_text(ptr - 1, ptr);
      break;
    case 'n': {
      const Char newline[] = {'\n'};
      handler.on_text(newline, newline + 1);
      break;
    }
    case 't': {
      const Char tab[] = {'\t'};
      handler.on_text(tab, tab + 1);
      break;
    }
    case 'a': handler.on_abbr_weekday(); break;
    case 'A': handler.on_full_weekday(); break;
    case 'w': handler.on_dec0_weekday(numeric_system::standard); break;
    case 'u': handler.on_dec1_weekday(numeric_system::standard); break;
    case 'b': handler.on_abbr_month(); break;
    case 'B': handler.on_full_month(); break;
    case 'H': handler.on_24_hour(numeric_system::standard); break;
    case 'I': handler.on_12_hour(numeric_system::standard); break;
    case 'M': handler.on_minute(numeric_system::standard); break;
    case 'S': handler.on_second(numeric_system::standard); break;
    case 'c': handler.on_datetime(numeric_system::standard); break;
    case 'x': handler.on_loc_date(numeric_system::standard); break;
    case 'X': handler.on_loc_time(numeric_system::standard); break;
    case 'D': handler.on_us_date(); break;
    case 'F': handler.on_iso_date(); break;
    case 'r': handler.on_12_hour_time(); break;
    case 'R': handler.on_24_hour_time(); break;
    case 'T': handler.on_iso_time(); break;
    case 'p': handler.on_am_pm(); break;
    case 'Q': handler.on_duration_value(); break;
    case 'q': handler.on_duration_unit(); break;
    case 'z': handler.on_utc_offset(); break;
    case 'Z': handler.on_tz_name(); break;
    case 'E':
      if (ptr == end) FMT_THROW(format_error("invalid format"));
      c = *ptr++;
      switch (c) {
      case 'c': handler.on_datetime(numeric_system::alternative); break;
      case 'x': handler.on_loc_date(numeric_system::alternative); break;
      case 'X': handler.on_loc_time(numeric_system::alternative); break;
      default: FMT_THROW(format_error("invalid format"));
      }
      break;
    case 'O':
      if (ptr == end) FMT_THROW(format_error("invalid format"));
      c = *ptr++;
      switch (c) {
      case 'w': handler.on_dec0_weekday(numeric_system::alternative); break;
      case 'u': handler.on_dec1_weekday(numeric_system::alternative); break;
      case 'H': handler.on_24_hour(numeric_system::alternative); break;
      case 'I': handler.on_12_hour(numeric_system::alternative); break;
      case 'M': handler.on_minute(numeric_system::alternative); break;
      case 'S': handler.on_second(numeric_system::alternative); break;
      default: FMT_THROW(format_error("invalid format"));
      }
      break;
    default:
      FMT_THROW(format_error("invalid format"));
    }
    begin = ptr;
  }
  if (begin != ptr) handler.on_text(begin, ptr);
  return ptr;
}
```
