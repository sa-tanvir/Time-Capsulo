```cpp
int format_float(T value, int precision, float_specs specs, buffer<char>& buf) {
  FMT_ASSERT(value >= 0, "value is negative");
  if (value == 0) {
    if (precision <= 0 || specs.format != float_format::fixed) {
      buf.push_back('0');
      return 0;
    }
    buf.resize(to_unsigned(precision));
    for (int i = 0; i < precision; ++i) buf[to_unsigned(i)] = '0';
    return -precision;
  }
  if (!specs.use_grisu || precision > 17)
    return snprintf_float(value, precision, specs, buf);
  const double v = static_cast<double>(value);
  char tmp[600];
  if (precision < 0) {
    // Shortest representation that round-trips.
    for (int n = 1; n <= 17; ++n) {
      std::snprintf(tmp, sizeof(tmp), "%.*e", n - 1, v);
      unsigned long long d = 0;
      const char* p = tmp;
      for (; *p && *p != 'e' && *p != 'E'; ++p)
        if (*p >= '0' && *p <= '9') d = d * 10 + static_cast<unsigned>(*p - '0');
      int e10 = (*p ? std::atoi(p + 1) : 0) - (n - 1);
      unsigned long long cands[3] = {d, d + 1, d > 1 ? d - 1 : 0};
      for (int k = 0; k < 3; ++k) {
        unsigned long long c = cands[k];
        if (c == 0) continue;
        char s[64];
        std::snprintf(s, sizeof(s), "%llue%d", c, e10);
        bool ok = specs.binary32
                      ? std::strtof(s, nullptr) == static_cast<float>(v)
                      : std::strtod(s, nullptr) == v;
        if (!ok) continue;
        while (c % 10 == 0) {
          c /= 10;
          ++e10;
        }
        char digits[24];
        int len = 0;
        while (c != 0) {
          digits[len++] = static_cast<char>('0' + c % 10);
          c /= 10;
        }
        buf.resize(to_unsigned(len));
        for (int i = 0; i < len; ++i) buf[to_unsigned(i)] = digits[len - 1 - i];
        return e10;
      }
    }
    return snprintf_float(value, precision, specs, buf);
  }
  if (specs.format == float_format::fixed) {
    std::snprintf(tmp, sizeof(tmp), "%.*f", precision, v);
    int len = 0;
    char digits[600];
    bool leading = true;
    for (const char* p = tmp; *p; ++p) {
      if (*p < '0' || *p > '9') continue;
      if (leading && *p == '0') continue;
      leading = false;
      digits[len++] = *p;
    }
    if (len == 0) digits[len++] = '0';
    buf.resize(to_unsigned(len));
    for (int i = 0; i < len; ++i) buf[to_unsigned(i)] = digits[i];
    return -precision;
  }
  // general / exp: precision significant digits, trailing zeros removed.
  if (precision < 1) precision = 1;
  std::snprintf(tmp, sizeof(tmp), "%.*e", precision - 1, v);
  char digits[32];
  int len = 0;
  const char* p = tmp;
  for (; *p && *p != 'e' && *p != 'E'; ++p)
    if (*p >= '0' && *p <= '9') digits[len++] = *p;
  int e10 = (*p ? std::atoi(p + 1) : 0) - (len - 1);
  while (len > 1 && digits[len - 1] == '0') {
    --len;
    ++e10;
  }
  buf.resize(to_unsigned(len));
  for (int i = 0; i < len; ++i) buf[to_unsigned(i)] = digits[i];
  return e10;
}
```
